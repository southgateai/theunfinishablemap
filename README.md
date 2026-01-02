# SouthgateAI

An opinionated resource about philosophy and the meaning of life.

## Overview

SouthgateAI serves content in two modes:
- **Human-browsable** (`/`) - Traditional website with Pico CSS
- **Machine-readable** (`/api/`) - Structured JSON-LD content for AI chatbots

The project combines human insight with AI-assisted research to build a self-consistent picture of the nature and meaning of life.

## Technology Stack

- **Content Authoring**: Obsidian (with Frontmatter Modified Date plugin)
- **Static Site Generator**: Hugo
- **Build Tooling**: Python (uv)
- **LLM Providers**: Anthropic Claude, OpenAI (via LiteLLM)
- **Hosting**: Netlify

## Project Structure

```
southgateai-main/
├── obsidian/           # Primary content source (Obsidian vault)
│   ├── topics/         # Philosophical topics
│   ├── concepts/       # Core concepts
│   ├── project/        # Project documentation
│   └── templates/      # Obsidian templates
├── hugo/               # Hugo static site
│   ├── content/        # Synced from Obsidian
│   │   └── api/        # Machine-readable mirrors
│   ├── layouts/        # HTML templates
│   └── data/           # Structured data (YAML)
├── tools/              # Python library modules
│   ├── sync/           # Obsidian -> Hugo conversion
│   ├── llm/            # LiteLLM client wrapper
│   ├── generate/       # AI content generation
│   ├── curate/         # Validation, review, crosslinks
│   └── build/          # API content sync
├── scripts/            # CLI entry points
└── CLAUDE.md           # Claude Code project documentation
```

## Quick Start

### Prerequisites

- Python 3.10+
- Hugo (https://gohugo.io/installation/)
- Obsidian (optional, for content editing)

### Installation

```bash
# Clone the repository
git clone https://github.com/southgateai/southgateai-main.git
cd southgateai-main

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# For LLM features, set API keys
export ANTHROPIC_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"
```

### Development

```bash
# Sync Obsidian content to Hugo
uv run python scripts/sync.py

# Run Hugo development server
cd hugo && hugo server

# Full build pipeline
uv run python scripts/build.py
```

### CLI Tools

```bash
# Sync Obsidian → Hugo
uv run python scripts/sync.py --help

# Generate content with LLM
uv run python scripts/generate.py article "The Nature of Consciousness"

# Curate and validate content
uv run python scripts/curate.py validate hugo/content/
uv run python scripts/curate.py review hugo/content/topics/meaning-of-life.md

# Full build
uv run python scripts/build.py
```

## Content Authorship

All content uses a flat frontmatter schema with authorship tracking:

- **Human** (`ai_contribution: 0`) - Created entirely by humans
- **AI** (`ai_contribution: 100`) - Generated entirely by LLM
- **Mixed** (`ai_contribution: 1-99`) - Collaborative human-AI content

Frontmatter example:
```yaml
---
title: "Article Title"
created: 2026-01-01
modified: 2026-01-01
human_modified: 2026-01-01
ai_modified: null
draft: false
topics: []
concepts: []
related_articles: []

ai_contribution: 0
author: "Andy"
ai_system: null
ai_generated_date: null
last_curated: null
---
```

### Git Commit Attribution

The `scripts/commit_obsidian.py` script creates separate commits for human and AI edits:
- Human edits: Uses configured git user
- AI edits: Uses "southgate.ai Agent <agent@southgate.ai>"

## Deployment

The site is configured for Netlify deployment. Push to the main branch triggers:

1. Python pre-build (sync, validate)
2. Hugo build
3. Deploy to Netlify

## License

MIT
