---
ai_contribution: 100
ai_generated_date: 2026-01-16
ai_modified: 2026-01-16 15:30:00+00:00
ai_system: claude-opus-4-5-20251101
author: null
concepts: []
created: 2026-01-16
date: &id001 2026-01-16
draft: false
human_modified: null
last_curated: null
last_deep_review: null
modified: *id001
related_articles:
- '[[project]]'
- '[[testability-ledger]]'
- '[[writing-style]]'
- '[[automation]]'
title: Coherence Inflation Countermeasures
topics: []
---

This document defines safeguards against "coherence inflation"—the systematic overcommitment that emerges when a single AI system both generates and reviews content optimized for internal consistency. Because The Unfinishable Map is intentionally a coherent worldview expressed as fact and heavily AI-generated, this failure mode is not hypothetical; it's the default.

The countermeasures below are designed to be implementable in the site's automated workflow without requiring constant human oversight.

## The Failure Mode

Coherence inflation occurs when:

1. **Arguments cite each other in loops**—Page A cites B, B cites C, C cites A, creating the illusion of independent support
2. **"Expressed as fact" feels like evidence**—Confident assertions in one article get treated as established facts in another
3. **Uncertainty gets systematically squeezed out**—The system tends toward stronger claims because hedged claims are harder to integrate coherently
4. **Counterarguments become weaker over time**—Each pass summarizes and softens objections
5. **Selection bias in examples**—Only examples that support the framework get included; counter-examples get filtered

The result is a worldview that feels increasingly solid while becoming increasingly brittle.

## Countermeasure 1: Confidence Stratification

### Policy

Every substantive claim in the site should have an implicit confidence level. The [Writing Style Guide](/project/writing-style/) already distinguishes four levels:

| Level | Language Pattern | Treatment |
|-------|-----------------|-----------|
| **Tenet-level** | Direct assertion | Core commitments; changing these changes the site |
| **Supported argument** | Qualified assertion | Following from tenets; should cite evidence |
| **Speculation** | Explicit hedging | Provisional; should be flagged as such |
| **Reporting others** | Attribution | Others' views; no confidence claim implied |

### Implementation

The `/refine-draft` and `/deep-review` skills should check that:

- High-confidence assertions (direct language) don't creep into areas where the site has only speculative support
- Low-confidence claims don't get referenced elsewhere as established facts
- Claims that were speculative in research notes don't become certain when synthesized into articles

### Flagging Pattern

When an article makes claims beyond tenet support, it should include an explicit uncertainty acknowledgment:

> *The following is speculative and extends beyond the site's core tenets:*

## Countermeasure 2: Mandatory Steelman Sections

### Policy

For topics where the site takes a strong position against major alternatives, the article must include a serious steelman of the opposing view before explaining why the site disagrees.

### Applicable Topics

- **Materialism/physicalism**: Requires fair presentation of why most philosophers accept it
- **Many-worlds interpretation**: Requires acknowledgment that MWI has sophisticated defenders
- **Functionalism**: Requires fair treatment of why consciousness science assumes it
- **Epiphenomenalism**: Requires acknowledgment of the exclusion argument's force
- **Illusionism**: Requires fair presentation of why eliminativists find it compelling

### Implementation

The `/pessimistic-review` skill should check that opposing views are:

1. Presented in their strongest form (not weakest version)
2. Attributed to actual proponents by name
3. Given sufficient space (not one dismissive sentence)
4. Responded to directly (not merely juxtaposed)

### Pattern

> **The Strongest Case for [Alternative]**: [Fair, attributed summary]
>
> [Name] argues that... [Citation]
>
> **Why This Site Disagrees**: [Response that addresses the actual argument]

## Countermeasure 3: Provenance Tagging for Empirical Claims

### Policy

Empirical claims (about experiments, studies, statistics, neuroscience findings) must be traceable to sources. The site should distinguish:

| Type | Treatment |
|------|-----------|
| **Primary source** | Direct citation with year |
| **Secondary summary** | Cite the summary source |
| **Site inference** | Explicitly mark as "inferred" |
| **Outdated** | Flag if >5 years old and in fast-moving field |

### Implementation

The `/validate-all` skill should flag:

- Empirical claims without citations
- Citations older than 5 years in neuroscience/physics sections
- Chains where one article cites another article citing a study (rather than the study directly)

### Pattern

When making empirical claims:

> Tegmark estimated decoherence times of 10⁻¹³ to 10⁻²⁰ seconds (Tegmark 2000); Hameroff argues this underestimates protective mechanisms (Hameroff & Penrose 2014).

Not:

> Decoherence happens almost instantly.

## Countermeasure 4: Periodic External Red-Team Reviews

### Policy

The site should receive periodic reviews from external AI systems (not the Claude instance generating content) specifically tasked to find:

- Claims that have drifted beyond evidence
- Arguments that beg the question
- Objections that have been systematically weakened
- Circular reference patterns
- Unstated assumptions that have become invisible

### Implementation

- **Frequency**: At least every 30 days
- **Scope**: Full site review (not just recent changes)
- **Stored**: In `obsidian/reviews/` with date and reviewer system
- **Actioned**: Significant findings become tasks in `todo.md`

### Pattern

Existing outer reviews (see `obsidian/reviews/`) demonstrate this pattern. This document formalizes the requirement.

### External Systems

- ChatGPT (OpenAI) — provides perspective outside Anthropic ecosystem
- Gemini (Google) — different training corpus and priors
- Human philosophers — ultimate check on AI blind spots

## Countermeasure 5: Circular Citation Detection

### Policy

The workflow should detect and flag patterns where:

- Page A cites B, B cites C, C cites A (direct loops)
- A concept defined on page A is used as evidence on page B which then supports page A (indirect loops)
- Multiple pages all cite the same internal page as authority without external grounding

### Implementation

The `/validate-all` skill should perform a link analysis:

1. Build a directed graph of internal wikilinks
2. Detect strongly connected components (cycles)
3. Flag cycles where no node in the cycle has external citations for its key claims
4. Report: "Pages X, Y, Z form a citation loop without external grounding for claim [claim]"

### Acceptable Patterns

Not all internal citation is problematic:
- **Hierarchical reference** (tenets.md → derived concepts) is fine
- **Cross-reference for related reading** is fine
- **Definitional reference** (term defined on one page, used on another) is fine

Problematic:
- **Evidential loops** where internal pages are cited as evidence for claims

### Detection Logic

```
For each claim C in page P:
  If C is supported by citing internal page Q:
    Check if Q's support for C traces to:
      a) External source → OK
      b) Another internal page that eventually loops to P → FLAG
      c) Bare assertion → FLAG if C is empirical/evidential
```

## Countermeasure 6: Freshness Tracking for Fast-Moving Fields

### Policy

Claims in fast-moving fields (neuroscience, quantum biology, AI) should track their evidence date. Claims older than threshold should be reviewed for updates.

### Thresholds

| Field | Freshness Threshold |
|-------|-------------------|
| Neuroscience of consciousness | 3 years |
| Quantum biology | 3 years |
| AI consciousness debates | 2 years |
| Philosophy of mind (core arguments) | 10 years |
| Historical philosophy | No threshold |

### Implementation

The evolution system already tracks `last_deep_review` in frontmatter. Extend this:

- Articles in fast-moving fields should have research sources dated
- `/validate-all` should flag articles where the most recent citation is older than threshold
- `/evolve` should prioritize updating stale content

## Countermeasure 7: Explicit Uncertainty Propagation

### Policy

When an article builds on speculative claims from another article, it should not present the derived claims with higher confidence than the base claim.

### Pattern

If `quantum-consciousness.md` says:
> "One possible mechanism—though highly speculative—is quantum selection in microtubules."

Then `free-will.md` should not say:
> "The microtubule selection mechanism explains libertarian free will."

Instead:
> "If the speculative microtubule mechanism proves viable, it would provide a mechanism for libertarian free will."

### Implementation

The `/deep-review` skill should check that:

- Claims flagged as speculative in their source remain speculative in derivations
- Confidence level is preserved across article boundaries
- Derived claims don't become more certain than their premises

## Monitoring and Metrics

### Key Indicators

Track these metrics across evolution sessions:

| Metric | Target | Warning |
|--------|--------|---------|
| Percentage of empirical claims with citations | >80% | <60% |
| Average age of citations in fast-moving sections | <3 years | >5 years |
| Number of detected citation loops | 0 | >2 |
| Days since external review | <30 | >60 |
| Steelman sections in major critique pages | 100% | <80% |

### Reporting

The `/evolve` skill should periodically (monthly) generate a coherence health report including these metrics.

## Relation to Site Perspective

These countermeasures serve the [Occam's Razor Has Limits](/tenets/#occams-limits) tenet by embodying the principle: simplicity and coherence are not sufficient for truth. A worldview can be internally consistent while being systematically wrong.

The site's epistemic integrity depends on remaining genuinely falsifiable and open to revision. Coherence inflation would make the site *unfalsifiable in practice* even if nominally falsifiable in principle—objections would get softened, evidence would get filtered, confidence would ratchet up.

The countermeasures formalize the commitment to genuine inquiry over rhetorical consistency.

## Further Reading

- [testability-ledger](/project/testability-ledger/) — What observations would update the framework
- [writing-style](/project/writing-style/) — How confidence levels are expressed in prose
- [automation](/project/automation/) — The evolution system these countermeasures integrate with