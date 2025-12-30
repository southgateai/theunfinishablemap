# SouthgateAI

An opinionated resource about philosophy and the meaning of life.

## Overview

SouthgateAI serves content in two modes:
- **Human-browsable** (`/`) - Traditional website experience
- **Machine-readable** (`/api/`) - Structured content for AI chatbots

## Technology Stack

- **Content Authoring**: Obsidian
- **Static Site Generator**: Hugo
- **Build Tooling**: Python
- **LLM Providers**: Anthropic Claude, OpenAI (configurable)
- **Hosting**: Netlify

## Project Structure

```
southgateai-main/
├── obsidian/           # Primary content source (Obsidian vault)
│   ├── topics/         # Philosophical topics
│   ├── concepts/       # Core concepts
│   ├── drafts/         # Work in progress
│   └── templates/      # Obsidian templates
├── hugo/               # Hugo static site
│   ├── content/        # Synced from Obsidian
│   ├── layouts/        # HTML templates
│   └── data/           # Structured data (YAML)
├── tools/              # Python tooling
│   ├── sync/           # Obsidian → Hugo sync
│   ├── llm/            # LLM provider abstraction
│   ├── generate/       # Content generation
│   └── curate/         # Content curation
└── scripts/            # CLI entry points
```

## Quick Start

### Prerequisites

- Python 3.10+
- Hugo (https://gohugo.io/installation/)
- Obsidian (optional, for content editing)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/southgateai-main.git
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

All content is marked with authorship metadata:

- **AI Generated** (`type: ai`) - Created entirely by LLM
- **Human Created** (`type: human`) - Written by humans
- **Mixed** (`type: mixed`) - Collaborative human-AI content

Frontmatter example:
```yaml
authorship:
  type: "mixed"
  ai_contribution: 30
  human_contributors:
    - name: "Andy"
      role: "author"
  ai_system: "claude-opus-4.5"
```

## Deployment

The site is configured for Netlify deployment. Push to the main branch triggers:

1. Python pre-build (sync, validate)
2. Hugo build
3. Deploy to Netlify

## License

MIT
