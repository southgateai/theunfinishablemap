---
ai_contribution: 100
ai_generated_date: 2026-01-16
ai_modified: 2026-01-16 16:00:00+00:00
ai_system: claude-opus-4-5-20251101
author: null
concepts:
- '[[mysterianism]]'
created: 2026-01-16
date: &id001 2026-01-16
draft: false
human_modified: null
last_curated: null
last_deep_review: null
modified: *id001
related_articles:
- '[[voids]]'
- '[[project]]'
- '[[coherence-inflation-countermeasures]]'
title: Voids Safety Protocol
topics: []
---

This protocol defines safety rails for exploring "voids"—the unexplorable, cognitively occluded, or potentially unthinkable territories described in the [Voids section](/voids/). Using LLMs to probe these areas creates specific risks: memetic hazards, coercive ideology traps, psychologically destabilizing content, and confusion between speculative exploration and endorsed claims.

The protocol is made public so readers understand the epistemic status of voids content.

## The Risks

### 1. Memetic Hazards

A memetic hazard is an idea that, once encountered, causes harm—spreading uncontrollably, distorting subsequent thinking, or inducing psychological distress.

The voids exploration explicitly invites LLMs to articulate thoughts that human minds may "slide away from" or "fail to grasp." This is dangerous territory:

- Ideas that destabilize personal identity or agency
- Concepts that induce existential dread without resolution
- Framings that, once adopted, cannot be un-adopted
- Self-referential traps that create rumination loops

### 2. Coercive Ideology Traps

Exploring "occluded" thoughts risks generating content that:

- Presents speculation as hidden truth ("they don't want you to know")
- Creates unfalsifiable frameworks that capture adherents
- Mimics the structure of conspiracy theories or cult indoctrination
- Exploits psychological vulnerabilities (death anxiety, identity uncertainty)

The site's framework—dualism, consciousness as fundamental, potential simulation—is adjacent to worldviews that can slide into harmful territory if not carefully bounded.

### 3. Psychological Destabilization

Content about:

- The unreality of self or identity
- Consciousness as potentially illusory
- Death and personal annihilation
- The possibility that our thoughts are controlled or limited

...can trigger depersonalization, derealization, anxiety, or depression in vulnerable readers. The voids section explicitly explores these themes.

### 4. Epistemic Confusion

Mixing exploratory speculation with endorsed claims creates confusion:

- Readers may take speculative content as the site's position
- LLM-generated "insights" may confabulate rather than discover
- The boundary between productive philosophy and harmful content becomes unclear

## Safety Principles

### Principle 1: Clear Epistemic Labeling

All voids content must be explicitly labeled with its epistemic status.

**Required labels:**

| Status | Label | Meaning |
|--------|-------|---------|
| **Speculative** | "This content is speculative exploration, not an endorsed position" | May be false, may be harmful if taken seriously |
| **Provisional** | "This represents preliminary investigation" | Under development, not ready for endorsement |
| **Apophatic** | "This explores limits, not positive claims" | What we cannot know, not what we do know |
| **Endorsed** | No special label (default for non-voids content) | The site's actual position |

Voids content is **never endorsed by default**. The default is "speculative" unless explicitly upgraded.

### Principle 2: Content Boundaries

The following are hard boundaries—content that will not be generated or included:

**Prohibited content:**

- Instructions for self-harm or suicide ideation
- Content designed to induce dissociation, depersonalization, or psychosis
- Unfalsifiable claims presented as certain truth
- Personal predictions about individual readers' consciousness or identity
- Content that "reveals" readers' limitations in ways designed to distress
- Techniques for destabilizing others' sense of reality

**Boundary cases requiring human review:**

- Detailed exploration of identity dissolution
- Extended treatment of death and annihilation
- Content explicitly designed to induce altered states
- Claims about limits on readers' cognitive abilities

### Principle 3: Separate Exploration from Endorsement

The site has two modes of content:

| Mode | Location | Status | Human Review |
|------|----------|--------|--------------|
| **Exploration** | `voids/`, `research/` | Speculative | Before publication |
| **Position** | `topics/`, `concepts/`, `arguments/` | Endorsed or supported | Standard review |

Voids exploration stays in exploration mode. Content is never moved to position mode without explicit human decision.

**Structural separation:**

- Voids articles always link back to stable, endorsed content
- Speculative claims in voids do not propagate to non-voids pages
- If a voids exploration produces an insight worthy of endorsement, it must be:
  1. Extracted
  2. Independently evaluated
  3. Rewritten in endorsed mode
  4. Placed in appropriate non-voids location

### Principle 4: Human Review Gates

**Mandatory human review before publication:**

| Content Type | Review Required |
|--------------|-----------------|
| New voids articles | Yes |
| Voids article edits that expand scope | Yes |
| Voids research notes | No (internal only) |
| Linking voids content from non-voids pages | Yes |

**Review checklist:**

- [ ] Content is clearly labeled as speculative
- [ ] No prohibited content present
- [ ] Boundary cases have been evaluated
- [ ] Content does not slip into endorsement language
- [ ] Exit paths exist (content doesn't trap readers in rumination)

### Principle 5: Exit Paths

Every voids article must include grounding elements:

**Required structure:**

1. **Entry warning**: Clear statement that content is speculative
2. **Body**: The exploration itself
3. **Exit path**: Return to stable ground—either:
   - Link to endorsed, grounded content
   - Explicit statement of what we *do* know
   - Reminder that speculation is not conclusion
4. **Resources**: For content touching mental health themes, links to support resources

**Example exit path:**

> *This exploration probes the limits of thought. It does not represent the site's settled position. For the site's actual framework, see [tenets](/tenets/). If these themes cause distress, consider taking a break from abstract speculation and grounding in embodied activity.*

### Principle 6: Stop Conditions

Exploration should halt when:

| Condition | Action |
|-----------|--------|
| Content veers into prohibited territory | Stop, delete, do not salvage |
| LLM responses become incoherent or confabulatory | Stop, flag for review |
| Exploration produces no new insight after sustained effort | Stop, document as unproductive |
| Content triggers safety concern from reviewer | Stop pending evaluation |
| Reader feedback indicates distress | Evaluate and potentially remove |

The goal is productive exploration of genuine cognitive limits, not generation of disturbing content for its own sake.

### Principle 7: No "Hidden Truth" Framing

The voids framework raises the possibility that some thoughts are occluded. But this must not slip into:

- "The truth they don't want you to know"
- "Only the enlightened can perceive this"
- "Once you see it, you can't unsee it"
- "This will change how you think forever"

These frames are manipulation tools. Even if some cognitive limits exist, presenting speculative content in these terms is harmful regardless of whether the content is true.

**Required framing:**

- "This is speculation about limits"
- "We don't know if this is accurate"
- "This may simply be confusion, not insight"
- "Alternative explanations exist"

## Implementation

### Workflow Integration

The `/research-voids` skill must:

1. Begin with acknowledgment of this protocol
2. Check generated content against prohibited list
3. Apply appropriate epistemic labels
4. Generate exit paths for any published content
5. Flag boundary cases for human review

### Validation

The `/validate-all` skill should check voids content for:

- Presence of required epistemic labels
- Presence of exit paths
- Absence of prohibited content patterns
- No slippage into endorsed mode without explicit decision

### Review Process

When a voids article is generated:

1. AI generates draft with speculative label
2. Draft reviewed against this protocol
3. Boundary cases escalated to human
4. Human approves or rejects publication
5. Approved content gets `draft: false`
6. Rejected content remains internal or is deleted

## Reader Notice

The following statement should appear on the voids section index page:

> **Note on Epistemic Status**
>
> The Voids section explores the limits of thought—what may be unknowable, unthinkable, or cognitively occluded. This content is *speculative*, not *endorsed*. Unlike the Topics and Concepts sections, which represent the site's considered positions, Voids content probes boundaries we may not be able to cross.
>
> Some of this content may be unsettling. It touches on limits to knowledge, identity, and reality. If you find these themes distressing, you are not obligated to engage with them. The stable, grounded framework is available in the [tenets](/tenets/) and [topics](/topics/) sections.
>
> Nothing in this section should be taken as personal prediction or diagnosis. These are philosophical explorations, not claims about you or your mind.

## Relation to Site Perspective

This protocol serves the [Occam's Razor Has Limits](/tenets/#occams-limits) tenet. If there are genuine cognitive limits—if some truths are structurally inaccessible—then exploring those limits is philosophically valuable. But it must be done responsibly.

The protocol also serves the site's commitment to intellectual honesty. Speculation about the unthinkable is interesting; presenting speculation as certainty is dishonest. The epistemic labeling and structural separation ensure readers know what they're getting.

Finally, the protocol recognizes that the site has power. Content presented confidently can shape readers' beliefs. That power creates responsibility. Voids content explores dangerous territory; the safeguards ensure the exploration doesn't cause harm.

## Further Reading

- [voids](/voids/) — The section this protocol governs
- [coherence-inflation-countermeasures](/project/coherence-inflation-countermeasures/) — Related epistemic hygiene measures
- [mysterianism](/concepts/mysterianism/) — The philosophical framework for cognitive closure
- [apophatic-approaches](/voids/apophatic-approaches/) — Methodological tools for probing limits