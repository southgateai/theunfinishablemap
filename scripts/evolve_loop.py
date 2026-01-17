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
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Module-level logger
log = logging.getLogger("evolve_loop")


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
    """Count commits ahead of origin."""
    result = subprocess.run(
        ["git", "rev-list", "--count", "@{u}..HEAD"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    if result.returncode != 0:
        return 0
    return int(result.stdout.strip())


def git_push() -> bool:
    """Push to origin. Returns True on success."""
    result = subprocess.run(
        ["git", "push"],
        cwd=Path(__file__).parent.parent,
    )
    return result.returncode == 0


def run_evolve(verbose: bool = True) -> bool:
    """Run a single evolve iteration. Returns True on success."""
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--output-format",
        "text",
    ]
    if verbose:
        cmd.append("--verbose")
    cmd.extend(["-p", "Run the evolve skill"])

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


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
        default=3600,
        help="Minimum seconds between git pushes (default: 3600 = 60 minutes)",
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
        default=Path(__file__).parent.parent.parent / "theunfinishablemap_log" / "evolve_loop.log",
        help="Log file path (default: ../theunfinishablemap_log/evolve_loop.log)",
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
    last_push_time: float | None = None

    log.info("=" * 60)
    log.info("Evolution Loop Started")
    log.info(f"  Evolve interval: {format_duration(args.interval)}")
    log.info(f"  Push interval: {format_duration(args.push_interval)} (minimum)")
    log.info(f"  Max iterations: {args.max_iterations or 'unlimited'}")
    log.info(f"  Log file: {args.log_file}")
    log.info("=" * 60)

    try:
        while True:
            iterations += 1
            iter_start = time.time()

            # Check if we've hit max iterations
            if args.max_iterations and iterations > args.max_iterations:
                log.info(f"Reached max iterations ({args.max_iterations})")
                break

            # Status header
            log.info("")
            log.info("─" * 60)
            log.info(f"Iteration {iterations}")
            log.info(f"Stats: {successes} succeeded, {failures} failed")
            log.info(f"Runtime: {format_duration(time.time() - start_time)}")
            log.info("─" * 60)

            try:
                # Run evolve
                log.info("Running /evolve...")
                if run_evolve(verbose=not args.quiet):
                    successes += 1
                    log.info("Evolve completed successfully")
                else:
                    failures += 1
                    log.warning("Evolve failed")

                # Check if we should push
                unpushed = get_unpushed_commits()
                now = time.time()
                seconds_since_push = (now - last_push_time) if last_push_time else float("inf")

                if unpushed > 0:
                    if seconds_since_push >= args.push_interval:
                        log.info(f"Pushing {unpushed} commit(s)...")
                        if git_push():
                            last_push_time = now
                            log.info("Push completed")
                        else:
                            log.warning("Push failed")
                    else:
                        remaining = args.push_interval - seconds_since_push
                        log.info(f"{unpushed} unpushed commit(s), next push in {format_duration(remaining)}")

            except Exception as e:
                failures += 1
                log.exception(f"Exception during iteration: {e}")

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
    unpushed = get_unpushed_commits()
    if unpushed > 0:
        log.info(f"Pushing final {unpushed} commit(s)...")
        git_push()

    return 0


if __name__ == "__main__":
    sys.exit(main())
