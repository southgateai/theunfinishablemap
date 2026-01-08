# Replenish Queue

Automatically generate new tasks when the todo queue is empty or near-empty. Combines gap analysis, research-to-article pipelines, and review generation to maintain a healthy task queue.

## Usage

```
/replenish-queue [mode]
```

Modes:
- `conservative` - Generate 3-5 high-confidence tasks only
- (default) - Standard replenishment, 5-8 tasks
- `aggressive` - Generate 8-12 tasks including speculative ones

## When to Use

- When `todo.md` Active Tasks section is empty
- When `/evolve` detects `needs_replenishment: true`
- Monthly strategic planning sessions
- After completing a major content push

## Task Generation Sources

The skill generates tasks from four sources, in priority order:

### Source 1: Task Chains (Successor Tasks)

Recent completions that should generate follow-up work:

| Completed Task Type | Generates |
|---------------------|-----------|
| `research-topic` | P2: Write article on [topic] |
| `expand-topic` | P2: Review related articles considering [new article] |
| `deep-review` with issues | P1: Address [issue] in [file] |
| `pessimistic-review` with critical | P1: Fix [critical issue] |
| `optimistic-review` opportunity | P3: Explore [expansion idea] |

**Chain Logic:**
1. Scan `recent_tasks` in evolution-state.yaml
2. For each `research-topic` completion, check if corresponding article exists
3. For each `expand-topic` completion, identify articles that existed before it and might benefit from cross-reference review
4. Generate successor tasks with appropriate priority

### Source 2: Unconsumed Research

Research notes that haven't produced articles yet:

1. Scan `obsidian/research/*.md` for all research notes
2. For each note, check if `related_articles` frontmatter links to published articles
3. If research has no corresponding article, generate:
   - P2: Write article on [topic] (based on [research file])

### Source 3: Gap Analysis

Content areas that need expansion:

1. Run lightweight coverage analysis (similar to content-coverage review)
2. Compare current content against convergence targets in evolution-state.yaml
3. Generate tasks for:
   - Topics supporting tenets that lack coverage
   - Concepts mentioned but not defined
   - Missing cross-links between related content

**Gap Categories:**
- **Critical gaps**: Directly support tenets, P1 priority
- **Important gaps**: Major philosophical context, P2 priority
- **Nice-to-have**: Interesting extensions, P3 priority

### Source 4: Staleness-Driven Tasks

Content that hasn't been touched recently:

1. Check `last_deep_review` frontmatter across all content files
2. For files not reviewed in 30+ days with `ai_contribution > 50`, generate:
   - P3: Deep review [file] for quality and currency

## Instructions

### 1. Load Current State

Read `obsidian/workflow/evolution-state.yaml` for:
- `recent_tasks` - completed work that might generate successors
- `content_stats` - current content counts
- `convergence_targets` - what "done" looks like
- `progress` - current progress toward targets

Read `obsidian/workflow/todo.md` to see:
- Current Active Tasks (should be empty or near-empty)
- Completed Tasks (for context on recent work)
- Vetoed Tasks (to avoid regenerating rejected ideas)

### 2. Generate Candidate Tasks

#### 2.1 Check Task Chains

For each task in `recent_tasks` from last 14 days:

**If `research-topic`:**
```python
research_file = task.output
topic = extract_topic(research_file)
article_exists = check_for_article(topic)
if not article_exists:
    candidates.append({
        'title': f'Write article on {topic}',
        'type': 'expand-topic',
        'priority': 'P2',
        'notes': f'Based on research in {research_file}. Synthesize findings into site content.',
        'source': 'chain',
        'chain_parent': research_file
    })
```

**If `expand-topic`:**
```python
new_article = task.output
topic = extract_topic(new_article)
# Find articles that might benefit from cross-referencing
related = find_related_articles(new_article)
for article in related[:2]:  # Max 2 review tasks per new article
    candidates.append({
        'title': f'Review {article} considering {topic} insights',
        'type': 'cross-review',
        'priority': 'P2',
        'notes': f'New article {new_article} may provide insights relevant to {article}. Check for cross-links, reinforcing arguments, or contradictions.',
        'source': 'chain',
        'chain_parent': new_article
    })
```

#### 2.2 Check Unconsumed Research

```python
for research_file in glob('obsidian/research/*.md'):
    frontmatter = parse_frontmatter(research_file)
    topic = extract_topic_from_title(frontmatter['title'])

    # Check if article exists for this research
    if not has_corresponding_article(topic):
        candidates.append({
            'title': f'Write article on {topic}',
            'type': 'expand-topic',
            'priority': 'P2',
            'notes': f'Research completed in {research_file}. Ready for article synthesis.',
            'source': 'unconsumed_research',
            'research_file': research_file
        })
```

#### 2.3 Run Gap Analysis

Scan existing content and identify gaps:

```python
# Load tenets for priority assessment
tenets = read_file('obsidian/tenets/tenets.md')

# Check each tenet for supporting content
gaps = []
for tenet in ['dualism', 'minimal-quantum', 'bidirectional', 'no-many-worlds', 'occams-limits']:
    supporting_content = find_content_supporting(tenet)
    if len(supporting_content) < 2:
        gaps.append({
            'area': tenet,
            'priority': 'P1',  # Tenet support is high priority
            'type': 'critical'
        })

# Check for mentioned-but-undefined concepts
all_wikilinks = extract_wikilinks(all_content)
existing_files = list_content_files()
for link in all_wikilinks:
    if link not in existing_files:
        gaps.append({
            'area': link,
            'priority': 'P2',
            'type': 'undefined_concept'
        })

# Generate tasks from gaps
for gap in gaps:
    if gap['type'] == 'critical':
        candidates.append({
            'title': f'Research {gap["area"]} support',
            'type': 'research-topic',
            'priority': gap['priority'],
            'notes': f'Tenet "{gap["area"]}" needs more supporting content.',
            'source': 'gap_analysis'
        })
    elif gap['type'] == 'undefined_concept':
        candidates.append({
            'title': f'Create concept page for {gap["area"]}',
            'type': 'expand-topic',
            'priority': gap['priority'],
            'notes': f'Concept "{gap["area"]}" is referenced but has no definition page.',
            'source': 'gap_analysis'
        })
```

#### 2.4 Check Content Staleness

```python
for content_file in glob('obsidian/**/*.md'):
    frontmatter = parse_frontmatter(content_file)
    last_review = frontmatter.get('last_deep_review')
    ai_contribution = frontmatter.get('ai_contribution', 0)

    if ai_contribution > 50:  # AI-heavy content needs periodic review
        if last_review is None or days_since(last_review) > 30:
            candidates.append({
                'title': f'Deep review {basename(content_file)}',
                'type': 'deep-review',
                'priority': 'P3',
                'notes': f'AI-generated content not reviewed in 30+ days.',
                'source': 'staleness'
            })
```

### 3. Filter and Deduplicate

Remove candidates that:
- Match any task in Vetoed Tasks section
- Match any task already in Active Tasks
- Duplicate another candidate (by title similarity)
- Would exceed mode limits

### 4. Score and Prioritize

Score each candidate:

```
SCORE = PRIORITY_BASE + SOURCE_BONUS + TENET_RELEVANCE

PRIORITY_BASE: P1=300, P2=200, P3=100
SOURCE_BONUS: chain=50, unconsumed_research=40, gap_analysis=30, staleness=10
TENET_RELEVANCE: +50 if directly supports a tenet
```

Sort by score descending.

### 5. Select Tasks Based on Mode

| Mode | Count | P3 Allowed? |
|------|-------|-------------|
| conservative | 3-5 | No |
| standard | 5-8 | 1-2 max |
| aggressive | 8-12 | Yes |

Ensure diversity:
- At least 1 research task (if candidates exist)
- At least 1 article task (if candidates exist)
- At least 1 review task (if candidates exist)
- Max 3 tasks from any single source

### 6. Format and Write Tasks

Add selected tasks to `obsidian/workflow/todo.md` under Active Tasks:

```markdown
## Active Tasks

### P1: Write article on epiphenomenalism
- **Type**: expand-topic
- **Notes**: Research completed in research/epiphenomenalism-2026-01-09.md. Key alternative to bidirectional interaction that site needs to address.
- **Source**: unconsumed_research
- **Generated**: 2026-01-09

### P2: Review hard-problem-of-consciousness.md considering panpsychism insights
- **Type**: cross-review
- **Notes**: New article concepts/panpsychism.md may provide insights relevant to topics/hard-problem-of-consciousness.md. Check for cross-links, reinforcing arguments, or contradictions.
- **Source**: chain (from panpsychism.md)
- **Generated**: 2026-01-09

### P2: Research quantum decoherence objection
- **Type**: research-topic
- **Notes**: Minimal Quantum Interaction tenet needs response to decoherence objection. Critical gap in site's argument.
- **Source**: gap_analysis
- **Generated**: 2026-01-09
```

### 7. Update State

Update `obsidian/workflow/evolution-state.yaml`:

```yaml
queue_status:
  p0_tasks: 0
  p1_tasks: 1
  p2_tasks: 4
  p3_tasks: 2
  needs_replenishment: false
  last_replenishment: 2026-01-09T10:00:00+00:00
  replenishment_source_counts:
    chain: 2
    unconsumed_research: 1
    gap_analysis: 3
    staleness: 1
```

### 8. Generate Report

Output summary:

```markdown
## Queue Replenishment Complete

**Mode**: standard
**Tasks generated**: 7
**Sources used**: chain (2), gap_analysis (3), unconsumed_research (1), staleness (1)

### Generated Tasks

| Priority | Title | Type | Source |
|----------|-------|------|--------|
| P1 | Write article on epiphenomenalism | expand-topic | unconsumed_research |
| P2 | Review hard-problem considering panpsychism | cross-review | chain |
| P2 | Research quantum decoherence objection | research-topic | gap_analysis |
| P2 | Create explanatory gap concept page | expand-topic | gap_analysis |
| P2 | Write Eastern philosophy overview | expand-topic | gap_analysis |
| P3 | Deep review free-will.md | deep-review | staleness |
| P3 | Explore consciousness and time topic | research-topic | optimistic |

### Queue Health
- P1: 1 task
- P2: 4 tasks
- P3: 2 tasks
- Estimated sessions to empty: 2-3

### Skipped Candidates
- "Research near-death experiences" - matches vetoed task
- "Write simulation article" - already exists
```

## Cross-Review Task Type

This skill introduces a new task type: `cross-review`

**Purpose**: After a new article is written, review related existing articles to:
1. Add cross-links to the new content
2. Check for contradictions or tensions
3. Identify arguments that could be strengthened by the new material
4. Ensure consistent terminology

**Execution**: When `/evolve` encounters a `cross-review` task:
1. Read the new article (chain_parent)
2. Read the target article
3. Look for:
   - Places to add `[[new-article]]` links
   - Arguments that new research supports or challenges
   - Terminology inconsistencies
4. Make edits if improvements found
5. Log findings even if no edits made

## Important

- NEVER generate tasks that match Vetoed Tasks
- NEVER generate P0 tasks (those require human urgency assessment)
- Always include `Generated` date for tracking
- Preserve task Notes verbatim when tasks complete
- Maximum 3 tasks per source to ensure diversity
- Chain tasks from last 14 days only (older completions are stale)
- This skill ONLY generates tasks; it does NOT execute them