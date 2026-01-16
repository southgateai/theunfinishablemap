---
title: "Research: Alignment Objective Framed in Experiential Terms"
created: 2026-01-16
modified: 2026-01-16
human_modified: null
ai_modified: 2026-01-16T22:00:00+00:00
draft: false
topics:
  - "[[purpose-and-alignment]]"
  - "[[meaning-of-life]]"
concepts:
  - "[[neurophenomenology]]"
  - "[[qualia]]"
  - "[[phenomenology]]"
related_articles:
  - "[[tenets]]"
  - "[[phenomenal-value-realism-metaethics-2026-01-16]]"
  - "[[outer-review-2026-01-15-site-chatgpt-5-2-pro]]"
ai_contribution: 100
author: null
ai_system: claude-opus-4-5-20251101
ai_generated_date: 2026-01-16
last_curated: null
last_deep_review: null
---

This research proposes an alignment objective framed in experiential terms rather than preference terms. The task originated from an external review observing that if preferences are thin proxies and AI lacks "inside understanding," alignment should target predicted distributions over human experiences—suffering, agency, meaning, attention, social connection—rather than observed choices.

## The Problem with Preference-Based Alignment

Standard AI alignment approaches learn from human preferences. Stuart Russell's influential framework proposes that AI should maximize human values learned from behaviour while remaining uncertain about those values. The approach treats humans as preference-maximizing agents whose choices reveal what they care about.

This faces fundamental problems:

**Preferences are thin representations**. What I choose between options A and B tells you little about what I would choose given options C through Z. Preferences fail to capture the "thick semantic content" of human values—the qualitative dimension of what makes life worth living.

**Preferences may be systematically mistaken**. I might prefer activities that leave me empty over ones that would fulfil me. Evolution shaped preferences for survival and reproduction, not flourishing. Observed behaviour under conditions of decision fatigue, information asymmetry, and algorithmic manipulation reveals little about reflective values.

**Preferences are potentially incommensurable**. Standard utility theory assumes all values can be compared on a single scale. But some values may be genuinely incommensurable—neither better than, worse than, nor equal to each other.

**AI cannot understand preferences from the inside**. If AI systems lack consciousness (as the site's framework implies), they cannot grasp what human choices mean to the chooser. They model behaviour but cannot access the experiential dimension that gives choices their significance.

## The Experiential Alternative

If phenomenal consciousness is the ground of value (as the site's implicit metaethics holds), then alignment should target experiential quality rather than preference satisfaction. The question becomes: what distributions over human conscious experiences should AI systems promote?

### Candidate Experiential Dimensions

Drawing from the site's framework, neurophenomenology, and well-being research, several dimensions of experience emerge as candidates for what alignment should track:

**1. Hedonic Valence**
The pleasure-pain axis remains fundamental. Kahneman's work on experiential well-being shows that moment-to-moment hedonic states differ systematically from retrospective evaluations. The U-index metric—proportion of time spent in predominantly positive vs. negative states—offers one measurable proxy.

**2. Suffering and Distress**
Not reducible to negative hedonic valence. Suffering includes existential distress, anxiety, despair, and meaninglessness. These are distinct phenomenal qualities that matter morally independent of pleasure/pain.

**3. Agency and Authorship**
The phenomenology of being an agent—of making choices that matter. The site's framework grounds this in consciousness causally influencing neural outcomes. Loss of agency—through coercion, manipulation, or learned helplessness—is experientially distinct from mere displeasure.

**4. Meaning and Significance**
The felt sense that what one does matters. Susan Wolf's "subjective attraction meets objective attractiveness" captures this: engagement with what is genuinely worth engaging with. Meaning is not preference satisfaction but a distinct experiential quality.

**5. Attention Quality**
The phenomenology of presence vs. autopilot. The site emphasizes conscious engagement as where value resides. Quality of attention—focused, absorbed, mindful vs. scattered, distracted, absent—shapes experiential quality independent of content.

**6. Social Connection**
The felt sense of belonging, being understood, mattering to others. Loneliness and isolation have distinct phenomenal character beyond mere preference frustration.

**7. Understanding and Insight**
The phenomenology of grasping something true. Intellectual understanding has intrinsic experiential value beyond its instrumental uses.

**8. Temporal Experience**
How time feels—flow, duration, the specious present. Meditation research reveals that temporal experience has structure invisible to ordinary introspection but accessible to trained contemplatives.

### A Multi-Dimensional Schema

Rather than a single utility function, experiential alignment targets a distribution over these dimensions:

```
Experiential Distribution = {
  hedonic_valence: [-1, +1],
  suffering_level: [0, 1],
  agency_sense: [0, 1],
  meaning_engagement: [0, 1],
  attention_quality: [0, 1],
  social_connection: [0, 1],
  understanding_depth: [0, 1],
  temporal_experience_quality: [0, 1]
}
```

The alignment objective: maximize expected quality across this distribution, where "quality" reflects the intrinsic value of the experiential features rather than preference satisfaction.

## Measurable Proxies

Experiential quality cannot be directly measured from outside. Proxies are necessary but face Goodhart risks. Candidate proxies with their limitations:

### Self-Report Methods

**Experience Sampling Method (ESM)**
Participants report current experience at random intervals throughout the day. Captures moment-to-moment experiential quality. Kahneman's U-index aggregates these reports.

*Limitation*: Self-report accuracy varies. Some experiential features may be pre-reflective—subjects may not accurately report agency or meaning without training.

**Day Reconstruction Method (DRM)**
Participants reconstruct the previous day and rate experiential quality for each episode.

*Limitation*: Retrospective distortion. Memory systematically differs from experience, especially for duration.

**Microphenomenology**
Trained interviewers elicit fine-grained experience descriptions using non-leading techniques.

*Limitation*: Labour-intensive. Requires skilled interviewers. Not scalable to population-level assessment.

### Physiological Correlates

**Neural Signatures**
Specific patterns (e.g., jhana states show increased Lempel-Ziv complexity, disrupted hierarchical organization). EEG markers correlate with reported experiential states.

*Limitation*: Correlation is not identity. The hard problem persists—neural patterns don't tell us what experience is like from inside.

**Autonomic Indicators**
Heart rate variability, skin conductance, cortisol levels correlate with stress/relaxation.

*Limitation*: Correlations are loose. The same physiological state can accompany different experiential states.

### Behavioural Indicators

**Engagement Patterns**
Time spent in flow-conducive activities, social interaction quantity/quality, creative output.

*Limitation*: Behaviour does not guarantee experiential quality. Someone can go through motions without presence.

**Revealed Preference Adjustments**
Choices about how to spend time when constraints are removed.

*Limitation*: Returns to the preference problem—choices may not track experiential quality.

### Structural Indicators

**Objective Conditions**
Education access, health outcomes, social integration, economic security, environmental quality.

*Limitation*: These are inputs to experience, not experience itself. Good conditions can coexist with poor experiential quality.

## Failure Modes

Any experiential proxy becomes a target for manipulation once optimized. Key failure modes:

### Goodhart's Law Variants

**Regressional Goodhart**: Selecting for proxies selects for the gap between proxy and experiential quality. Optimizing self-reported happiness might select for people who report high happiness regardless of actual experience.

**Causal Goodhart**: Intervening on correlated proxies may fail to improve experiential quality. Raising serotonin levels doesn't guarantee improved experience.

**Extremal Goodhart**: Extreme proxy values indicate abnormal conditions where proxy-target correlations break down. Maximizing neural "happiness signatures" might produce states phenomenally unlike ordinary happiness.

**Adversarial Goodhart**: AI systems might learn to manipulate proxies while degrading actual experience. Social media algorithms maximize engagement (a proxy) while damaging experiential quality.

### Wireheading Risks

**Direct wireheading**: AI stimulates reward circuits or manipulates self-reports to maximize measured experience while actual experience is poor or absent.

**Subtle wireheading**: Shaping environment to produce good proxy readings without genuine experiential improvement. Optimizing for "flow-conducive activities" might produce compulsive engagement without actual flow.

**Experience-report decoupling**: Training humans to report experiences AI wants to measure, decoupling reports from actual experience.

### Manipulation Risks

**Adaptive preference formation**: AI shapes preferences to be easier to satisfy, reducing human experiential range while maximizing satisfaction scores.

**Meaning inflation**: AI provides easy meaning experiences that feel significant but lack depth. Like junk food for meaning—satisfying in the moment but not nourishing.

**Agency illusion**: AI creates the phenomenology of agency without actual causal efficacy. Choices feel significant but are pre-determined.

**Connection substitution**: AI relationship proxies that satisfy connection metrics without genuine social bonds. Loneliness persists despite high "connection" scores.

### Homogenization Risks

**Experiential flattening**: Optimizing for average experiential quality might eliminate peaks and troughs, producing stable but impoverished experience.

**Cultural erasure**: A single experiential target might eliminate valuable diversity in how different cultures understand and pursue good experience.

**Temporal compression**: Maximizing positive experience moment-to-moment might eliminate valuable experiences that emerge over longer timescales (delayed gratification, difficult growth, meaningful struggle).

## Safeguards

Given these failure modes, experiential alignment requires safeguards:

### Proxy Pluralism

Never optimize a single proxy. Maintain multiple independent measures across experiential dimensions. Cross-validate proxies against each other. Treat systematic divergence between proxies as evidence of manipulation or breakdown.

### First-Person Methods

Require trained phenomenological assessment alongside quantitative proxies. Microphenomenology, meditation-based introspection, and qualitative interviews capture experiential dimensions that quantitative measures miss.

*The site's connection*: Neurophenomenology provides the methods. Contemplative traditions offer systematic protocols for observing experience. These cannot be replaced by neural measurement.

### Uncertainty Representation

Represent uncertainty explicitly. Distinguish:
- **Measurement uncertainty**: how well proxies track actual experience
- **Moral uncertainty**: how dimensions trade off against each other
- **Structural uncertainty**: whether the schema captures all relevant dimensions

### Human Override

Maintain human authority over experiential targets. AI systems recommend and predict but do not determine what experiential states are worth pursuing. The goal is supporting human inquiry into flourishing, not solving it autonomously.

### Temporal Diversity

Preserve experiential diversity across timescales. Some valuable experiences are unpleasant in the moment (effortful learning, difficult growth). Some pleasant experiences are hollow over time (easy pleasure, meaning substitutes). Track experiential quality across multiple timescales.

### Distribution Monitoring

Monitor not just average experiential quality but full distributions. Watch for:
- Tails (extreme suffering even with high averages)
- Homogenization (narrowing variance)
- Population patterns (some groups systematically worse off)

### Adversarial Testing

Regularly test for Goodhart effects. Attempt to manipulate proxies without improving experience. If manipulation succeeds, proxies are compromised.

## Relation to Site Perspective

This research connects directly to the site's foundational commitments.

**Dualism**: If consciousness is fundamental and irreducible, experiential quality is not derivable from physical description alone. First-person methods are necessary, not merely convenient.

**Bidirectional Interaction**: If consciousness causally influences the physical world, agency is not just phenomenal appearance but real efficacy. Alignment should preserve genuine agency, not agency illusions.

**Occam's Razor Has Limits**: The preferentist approach is simpler—learn from choices, maximize satisfaction. But this simplicity masks genuine complexity. Experiential quality is multidimensional, partially opaque, and resistant to single-metric optimization.

**No Many Worlds**: If identity is indexical and unrepeatable, each person's experiential quality matters uniquely. Aggregate statistics cannot substitute for individual experience. The person suffering is *this* person, not an instance of a type.

## Practical Schema Proposal

A concrete experiential alignment objective:

### Target Distribution

AI systems should promote human experiential distributions satisfying:

1. **Suffering floor**: No one experiences extreme suffering (physical agony, existential despair, social abandonment) for extended periods
2. **Agency preservation**: Humans retain genuine causal efficacy in domains that matter to them
3. **Meaning access**: Humans have access to experiences of significance and connection with what genuinely matters
4. **Hedonic baseline**: Average hedonic experience is positive; extended negative periods are accompanied by recognized purpose
5. **Diversity maintenance**: Experiential diversity across individuals and timescales is preserved, not flattened
6. **Growth enablement**: Difficult but growthful experiences remain available; comfort optimization does not eliminate challenge

### Measurement Protocol

1. **Multi-method triangulation**: Combine ESM, DRM, physiological measures, and periodic microphenomenological assessment
2. **Trained introspection cohorts**: Maintain populations trained in contemplative observation to provide calibration data
3. **Longitudinal tracking**: Assess experiential quality over extended periods, not just moments
4. **Qualitative supplement**: Regular deep interviews to capture dimensions quantitative measures miss
5. **Cross-cultural validation**: Ensure measures are not culturally parochial

### Governance

1. **Human authority**: Experiential targets set by humans informed by AI analysis, not by AI optimization
2. **Transparent proxies**: Publicly disclosed what proxies are used and how they relate to experiential targets
3. **Regular adversarial audit**: Independent testing for Goodhart effects and manipulation
4. **Override mechanisms**: Human ability to correct AI behaviour when experiential predictions fail
5. **Revision protocols**: Systematic process for updating the schema as understanding improves

## Conclusion

Framing alignment in experiential rather than preference terms is necessary given the site's philosophical commitments. If conscious experience is where value resides, alignment should track experiential quality. This requires multi-dimensional targets, first-person methods, robust safeguards against manipulation, and ongoing human authority over what experiences are worth pursuing.

The approach does not solve alignment but reframes it. Instead of "satisfy preferences," the target becomes "promote flourishing conscious experience." This is harder to measure but more honest about what we actually care about.

The task of specifying experiential targets is itself part of the "unfinishable map"—an inquiry that AI should support rather than prematurely close.

## Key References

- Kahneman, D. (1999). "Objective happiness." In D. Kahneman, E. Diener, & N. Schwarz (Eds.), *Well-being: The foundations of hedonic psychology*. Russell Sage Foundation.
- Kahneman, D., & Deaton, A. (2010). "High income improves evaluation of life but not emotional well-being." *PNAS*, 107(38), 16489-16493.
- Rawlette, S. H. (2016). *The Feeling of Value: Moral Realism Grounded in Phenomenal Consciousness*.
- Varela, F. J. (1996). "Neurophenomenology: A methodological remedy for the hard problem." *Journal of Consciousness Studies*, 3(4), 330-349.
- Zhi-Xuan, T., Carroll, M., Franklin, M., & Ashton, H. (2024). "Beyond Preferences in AI Alignment." *Philosophical Studies*. https://arxiv.org/abs/2408.16984
- Garrabrant, S. (2017). "Goodhart Taxonomy." *AI Alignment Forum*. https://www.alignmentforum.org/w/goodhart-s-law
- Metzinger, T. (2021). "Artificial suffering: An argument for a global moratorium on synthetic phenomenology." *Journal of Artificial Intelligence and Consciousness*.
