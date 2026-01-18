# The Unfinishable Map

[![Netlify Status](https://api.netlify.com/api/v1/badges/bc29448a-9065-476b-9659-5d81f3b963c8/deploy-status)](https://app.netlify.com/projects/unfinishablemap/deploys)

> **⚠️ Claude Code Permissions Warning**
>
> This repository includes `.claude/settings.json` which pre-approves certain Claude Code operations (bash commands, skills, web access). If you don't want Claude to have these permissions when working in this repository, delete the `.claude/settings.json` file before running Claude Code.

A philosophical content platform exploring consciousness, meaning, and what it is to be human. Not balanced. Not hedged. Just our best guess at the truth, revised as we learn.

**Live site:** https://unfinishablemap.org

## Overview

The Unfinishable Map is a project to build a coherent worldview grounded in five foundational tenets:

1. **Dualism** — Consciousness is not reducible to physical processes
2. **Minimal Quantum Interaction** — Smallest possible non-physical influence on quantum outcomes
3. **Bidirectional Interaction** — Consciousness causally influences the physical world
4. **No Many Worlds** — Reject MWI; indexical identity matters
5. **Occam's Razor Has Limits** — Simplicity is unreliable with incomplete knowledge

The project combines human insight with AI-assisted research, with all content tracking its authorship (human, AI, or mixed).

## Technology Stack

- **Content Authoring**: Obsidian (with Frontmatter Modified Date plugin)
- **Static Site Generator**: Hugo
- **Build Tooling**: Python (uv)
- **AI Assistance**: Claude Code (for content generation and review)
- **Hosting**: Netlify

## Project Structure

```
unfinishablemap/
├── obsidian/           # Primary content source (Obsidian vault)
│   ├── tenets/         # Foundational commitments
│   ├── topics/         # Deep dives (hard problem, free will, meaning of life...)
│   ├── concepts/       # Core ideas (qualia, functionalism, IIT...)
│   ├── arguments/      # Arguments against competing views
│   ├── voids/          # The unexplored, unexplorable, and occluded
│   ├── research/       # AI research notes with sources
│   ├── workflow/       # AI automation (todo queue, changelog, reviews)
│   └── project/        # Project documentation
├── archive/            # Archived content (preserves URLs for external links)
│   ├── topics/         # Mirrors obsidian structure
│   ├── concepts/
│   └── ...             # Pages show archive notice linking to replacement
├── hugo/               # Hugo static site
│   ├── content/        # Synced from Obsidian + archive
│   ├── layouts/        # HTML templates
│   └── data/           # Structured data (YAML)
├── tools/              # Python library modules
├── scripts/            # CLI entry points
├── .claude/            # Claude Code skills and configuration
│   └── skills/         # AI automation skills (/evolve, /research-topic, etc.)
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
git clone https://github.com/unfinishablemap/unfinishablemap.git
cd unfinishablemap

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
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

# Validate content frontmatter
uv run python scripts/validate.py hugo/content/

# Full build
uv run python scripts/build.py
```

## Content Authorship

All content uses a flat frontmatter schema with authorship tracking:

- **Human** (`ai_contribution: 0`) - Created entirely by humans
- **AI** (`ai_contribution: 100`) - Generated entirely by AI
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
- AI edits: Uses "unfinishablemap.org Agent <agent@unfinishablemap.org>"

## AI Automation

The project includes an AI automation system for content development. Key skills:

- `/evolve` — Main orchestrator: selects and executes tasks based on priority/staleness
- `/research-topic [topic]` — Web research producing structured notes
- `/expand-topic [topic]` — Generate new article (always as draft)
- `/deep-review [file]` — Comprehensive single-document review with improvements
- `/validate-all` — Daily health check: frontmatter, links, orphans

Tasks are managed in `obsidian/workflow/todo.md` with P0-P3 priorities. All AI-generated content is created as drafts requiring human review.

## Deployment

The site is configured for Netlify deployment. Push to the main branch triggers:

1. Python pre-build (sync, validate)
2. Hugo build
3. Deploy to Netlify

## Current Content

*As of 2026-01-18*

- **14 topics**: Hard problem, free will, meaning of life, personal identity, AI consciousness, Eastern philosophy, animal consciousness, death and consciousness, ethics of consciousness, and more
- **82 concepts**: Qualia, functionalism, IIT, panpsychism, epiphenomenalism, quantum consciousness, agent causation, libertarian free will, and more
- **4 arguments**: Against materialism, functionalism, epiphenomenalism, and many-worlds
- **5 voids articles**: Apophatic approaches, limits reveal structure, self-reference paradox, and more
- **83 research notes**: Sources and analysis for article development

## License

MIT
