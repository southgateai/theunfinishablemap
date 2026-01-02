# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SouthgateAI is a philosophical content platform that serves content in two modes:
- **Human-browsable** (`/`) - Traditional website via Hugo with Pico CSS
- **Machine-readable** (`/api/`) - Structured JSON-LD content for AI chatbots

**Data flow:** Obsidian vault → Python sync tools → Hugo content → Static site (Netlify)

## Commands

```bash
# Install dependencies
uv sync

# Full build pipeline (sync + validate + build Hugo)
uv run python scripts/build.py

# Sync Obsidian → Hugo only
uv run python scripts/sync.py

# Hugo dev server
cd hugo && hugo server

# Validate frontmatter
uv run python scripts/curate.py validate hugo/content/

# AI content review
uv run python scripts/curate.py review hugo/content/topics/meaning-of-life.md

# Generate article with LLM
uv run python scripts/generate.py article "Topic Name" --style exploratory

# Generate crosslinks between content
uv run python scripts/curate.py crosslink hugo/content/ --apply

# Commit obsidian changes with human/AI attribution
uv run python scripts/commit_obsidian.py --dry-run
uv run python scripts/commit_obsidian.py
```

## Architecture

```
obsidian/           # Primary content source (Obsidian vault)
├── topics/         # Philosophical topics
├── concepts/       # Core concepts
├── templates/      # Obsidian templates
└── project/        # Project documentation

hugo/               # Static site generator
├── content/        # Synced from Obsidian
│   └── api/        # Machine-readable mirrors
├── layouts/        # HTML templates
└── data/           # YAML data files

tools/              # Python library modules
├── sync/           # Obsidian → Hugo conversion
├── llm/            # LiteLLM client wrapper
├── generate/       # AI content generation
├── curate/         # Validation, review, crosslinks
└── build/          # API content sync

scripts/            # CLI entry points (thin wrappers calling tools/)
```

## Authorship Tracking

When editing files in `obsidian/`, update the `ai_modified` frontmatter field with the current ISO timestamp:

```yaml
ai_modified: 2026-01-02T15:30:00+03:00
```

The `human_modified` field is updated automatically by the Obsidian Frontmatter Modified Date plugin when the user edits.

The `commit_obsidian.py` script compares these timestamps to determine git commit authorship:
- Human edits: Uses configured git user
- AI edits: Uses "southgate.ai Agent <agent@southgate.ai>"

## Frontmatter Schema

All markdown content uses a flat schema (no nesting):

```yaml
---
title: "Article Title"
created: YYYY-MM-DD
modified: YYYY-MM-DD
human_modified: YYYY-MM-DD or ISO timestamp
ai_modified: null or ISO timestamp
draft: true/false
topics: []
concepts: []
related_articles: []

ai_contribution: 0-100   # 0=human, 100=ai, 1-99=mixed
author: "Name"           # human author
ai_system: null          # or model name like "claude-sonnet-4-20250514"
ai_generated_date: null  # when AI generated content
last_curated: null       # last human review date
---
```

Authorship type is derived from `ai_contribution`:
- `0` = human (purely human-created)
- `100` = ai (purely AI-generated)
- `1-99` = mixed (human-AI collaboration)

## Code Conventions

- **Python:** Ruff linting (E, F, I, N, W), line length 100, mypy type hints required
- **Module pattern:** `scripts/` contains thin CLI wrappers, `tools/` contains business logic
- **LLM calls:** Use `tools/llm/client.py` which wraps LiteLLM for multi-provider support
- **Content links:** Obsidian uses `[[wikilinks]]`, auto-converted to Hugo markdown links during sync
