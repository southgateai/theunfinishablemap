#!/usr/bin/env python3
"""
Continuous evolution loop for The Unfinishable Map.

Runs /evolve repeatedly with rate-limited git push to avoid excessive Netlify rebuilds.
"""

import argparse
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Module-level logger
log = logging.getLogger("evolve_loop")

# Repository root
REPO_ROOT = Path(__file__).parent.parent
STATE_PATH = REPO_ROOT / "obsidian" / "workflow" / "evolution-state.yaml"


class GitError(Exception):
    """Raised when a git command fails."""

    def __init__(self, command: str, returncode: int, stdout: str, stderr: str):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Git command failed: {command}")


class EvolveError(Exception):
    """Raised when the evolve command fails."""

    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Evolve failed with exit code {returncode}")


class EvolveTimeout(Exception):
    """Raised when the evolve command times out."""

    def __init__(self, timeout_seconds: int, stdout: str, stderr: str):
        self.timeout_seconds = timeout_seconds
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Evolve timed out after {timeout_seconds} seconds")


def setup_logging(log_file: Path) -> None:
    """Configure logging with console and rotating file handlers."""
    log.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)

    # Daily rotating file handler (keeps all logs)
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=0,  # Keep all logs
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    log.addHandler(file_handler)


def get_unpushed_commits() -> int:
    """Count commits ahead of origin. Raises GitError on failure."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "@{u}..HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise GitError(
            "git rev-list --count @{u}..HEAD",
            result.returncode,
            result.stdout,
            result.stderr,
        )
    return int(result.stdout.strip())


def git_push() -> None:
    """Push to origin. Raises GitError on failure."""
    result = subprocess.run(
        ["git", "push"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise GitError("git push", result.returncode, result.stdout, result.stderr)


def get_last_push_time() -> float | None:
    """Read last_git_push from evolution state. Returns Unix timestamp or None."""
    try:
        # Import here to avoid circular imports at module load time
        from tools.evolution.state import load_state

        state = load_state(STATE_PATH)
        if state.last_git_push is None:
            return None
        return state.last_git_push.timestamp()
    except Exception as e:
        log.warning(f"Could not read last_git_push from state: {e}")
        return None


def set_last_push_time() -> None:
    """Update last_git_push in evolution state to now."""
    try:
        from tools.evolution.state import load_state, save_state

        state = load_state(STATE_PATH)
        state.last_git_push = datetime.now(timezone.utc)
        save_state(state, STATE_PATH)
    except Exception as e:
        log.warning(f"Could not update last_git_push in state: {e}")


def run_evolve(verbose: bool = True, timeout_seconds: int = 5400) -> str:
    """Run a single evolve iteration. Returns claude output.

    Raises:
        EvolveError: If the command fails with non-zero exit code.
        EvolveTimeout: If the command exceeds timeout_seconds (default 90 minutes).
    """
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--output-format",
        "text",
    ]
    if verbose:
        cmd.append("--verbose")
    cmd.extend(["-p", "Run the evolve skill"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode("utf-8") if e.stdout else ""
        stderr = e.stderr.decode("utf-8") if e.stderr else ""
        raise EvolveTimeout(timeout_seconds, stdout, stderr) from e

    # Log the output regardless of success/failure
    output = result.stdout
    if result.stderr:
        output += "\n--- stderr ---\n" + result.stderr

    if result.returncode != 0:
        raise EvolveError(result.returncode, result.stdout, result.stderr)

    return output


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def main() -> int:
    parser = argparse.ArgumentParser(description="Continuous evolution loop")
    parser.add_argument(
        "--interval",
        type=int,
        default=2400,
        help="Seconds between evolve runs (default: 2400 = 40 minutes)",
    )
    parser.add_argument(
        "--push-interval",
        type=int,
        default=14400,
        help="Minimum seconds between git pushes (default: 14400 = 4 hours)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Stop after N iterations (0 = unlimited)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce claude output verbosity",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path(__file__).parent.parent.parent
        / "unfinishablemap_log"
        / "evolve_loop.log",
        help="Log file path (default: ../unfinishablemap_log/evolve_loop.log)",
    )
    args = parser.parse_args()

    # Ensure log directory exists
    args.log_file.parent.mkdir(parents=True, exist_ok=True)
    setup_logging(args.log_file)

    # Stats tracking
    iterations = 0
    successes = 0
    failures = 0
    start_time = time.time()

    # Read last push time from state (persisted across restarts, shared with tweet-highlight)
    last_push_time: float | None = get_last_push_time()

    log.info("=" * 60)
    log.info("Evolution Loop Started")
    log.info(f"  Evolve interval: {format_duration(args.interval)}")
    log.info(f"  Push interval: {format_duration(args.push_interval)} (minimum)")
    log.info(f"  Max iterations: {args.max_iterations or 'unlimited'}")
    log.info(f"  Log file: {args.log_file}")
    log.info("=" * 60)

    try:
        while True:
            # Check if we've hit max iterations
            if args.max_iterations and iterations >= args.max_iterations:
                log.info(f"Reached max iterations ({args.max_iterations})")
                break

            iterations += 1
            iter_start = time.time()

            # Status header
            log.info("")
            log.info("─" * 60)
            log.info(f"Iteration {iterations}")
            log.info(f"Stats: {successes} succeeded, {failures} failed")
            log.info(f"Runtime: {format_duration(time.time() - start_time)}")
            log.info("─" * 60)

            # Run evolve
            log.info(f"Running /evolve at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
            try:
                output = run_evolve(verbose=not args.quiet)
                successes += 1
                log.info("Evolve completed successfully")
                # Log a summary of the output (last 50 lines)
                output_lines = output.strip().split("\n")
                if len(output_lines) > 50:
                    log.info(f"Claude output ({len(output_lines)} lines, showing last 50):")
                    for line in output_lines[-50:]:
                        log.info(f"  {line}")
                else:
                    log.info(f"Claude output ({len(output_lines)} lines):")
                    for line in output_lines:
                        log.info(f"  {line}")
            except EvolveTimeout as e:
                failures += 1
                log.error(f"Evolve timed out after {e.timeout_seconds // 60} minutes")
                if e.stdout:
                    log.error("--- stdout (last 100 lines) ---")
                    for line in e.stdout.strip().split("\n")[-100:]:
                        log.error(f"  {line}")
                if e.stderr:
                    log.error("--- stderr ---")
                    for line in e.stderr.strip().split("\n"):
                        log.error(f"  {line}")
            except EvolveError as e:
                failures += 1
                log.error(f"Evolve failed with exit code {e.returncode}")
                if e.stdout:
                    log.error("--- stdout (last 100 lines) ---")
                    for line in e.stdout.strip().split("\n")[-100:]:
                        log.error(f"  {line}")
                if e.stderr:
                    log.error("--- stderr ---")
                    for line in e.stderr.strip().split("\n"):
                        log.error(f"  {line}")

            # Check if we should push
            try:
                unpushed = get_unpushed_commits()
                now = time.time()

                # Re-read last push time from state in case tweet-highlight pushed
                last_push_time = get_last_push_time() or last_push_time
                seconds_since_push = (now - last_push_time) if last_push_time else float("inf")

                if unpushed > 0:
                    if seconds_since_push >= args.push_interval:
                        log.info(f"Pushing {unpushed} commit(s)...")
                        try:
                            git_push()
                            set_last_push_time()  # Persist to state file
                            last_push_time = now
                            log.info("Push completed")
                        except GitError as e:
                            log.error(f"Push failed: {e.command}")
                            if e.stdout:
                                log.error(f"  stdout: {e.stdout.strip()}")
                            if e.stderr:
                                log.error(f"  stderr: {e.stderr.strip()}")
                    else:
                        remaining = args.push_interval - seconds_since_push
                        log.info(
                            f"{unpushed} unpushed commit(s), next push in {format_duration(remaining)}"
                        )
            except GitError as e:
                log.warning(f"Could not check unpushed commits: {e.command}")
                if e.stderr:
                    log.warning(f"  stderr: {e.stderr.strip()}")

            # Sleep until next iteration
            iter_duration = time.time() - iter_start
            sleep_seconds = max(0, args.interval - iter_duration)

            if sleep_seconds > 0:
                log.info(f"Sleeping {format_duration(sleep_seconds)} until next iteration...")
                time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        log.info("Interrupted by user")

    # Final stats
    log.info("")
    log.info("=" * 60)
    log.info("Evolution Loop Summary")
    log.info("=" * 60)
    log.info(f"  Total iterations: {iterations}")
    log.info(f"  Succeeded: {successes}")
    log.info(f"  Failed: {failures}")
    log.info(f"  Success rate: {successes / iterations * 100:.0f}%" if iterations else "N/A")
    log.info(f"  Total runtime: {format_duration(time.time() - start_time)}")

    # Final push if needed
    try:
        unpushed = get_unpushed_commits()
        if unpushed > 0:
            log.info(f"Pushing final {unpushed} commit(s)...")
            try:
                git_push()
                log.info("Final push completed")
            except GitError as e:
                log.error(f"Final push failed: {e.command}")
                if e.stderr:
                    log.error(f"  stderr: {e.stderr.strip()}")
    except GitError:
        pass  # Ignore errors checking unpushed at shutdown

    return 0


if __name__ == "__main__":
    sys.exit(main())