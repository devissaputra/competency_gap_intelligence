# Analytic system card

## System

Competency Gap Intelligence

## Purpose

Transparent competency-evidence review, gap prioritization, prerequisite-aware sequencing, and learning-resource matching for development planning.

## Current maturity

Working research prototype.

The bundled example is synthetic and demonstrates the software path only.

It does not establish that the proficiency scale, role requirements, confidence judgments, prerequisites, or resources are valid for a real workplace.

## Inputs

### Proficiency scale

- name
- minimum
- maximum

### Role requirements

- competency
- target
- importance
- optional framework/source
- optional rationale

### Competency evidence

- competency
- observed level
- source
- evidence type
- confidence
- date
- optional assessor

### Prerequisites

Directed competency dependencies.

### Resources

- id
- title
- competency
- entry level
- target level
- effort
- modality
- competency prerequisites

## Evidence aggregation

Multiple competency observations are combined with a confidence-weighted mean.

Evidence age and provenance remain available in the summary.

This is a transparent baseline rather than a psychometric claim.

## Gap outputs

Each role competency is classified as one of:

- gap
- met
- exceeds target
- unknown evidence
- insufficient evidence

Missing evidence is never converted to zero proficiency.

Stale or low-confidence evidence blocks automatic ranking.

## Priority

Confirmed gaps use:

`gap × importance`

The system also supports alternative importance scenarios so ranking sensitivity is visible.

## Prerequisites

Prerequisite graphs are validated for unknown nodes and cycles.

Development sequencing places required foundations before dependent gaps.

## Resource matching

Resources are matched only to confirmed gaps and only when:

- current level satisfies entry level
- the resource advances the competency
- declared competency prerequisites are met

The matching order is explicit and deterministic.

## Development-path outputs

The plan can recommend:

- collect evidence
- review evidence
- develop
- no development required

It also exposes prerequisite blockers and candidate resources.

## Main limitations

The system does not:

- infer competency from raw behavior
- validate a competency framework
- establish psychometric reliability
- prove that a resource will close a gap
- model learning-resource quality
- estimate training impact
- infer potential
- make employment decisions

Confidence weights, importance weights, scale levels, and prerequisite links are supplied assumptions.

## Evidence needed before real use

A real implementation needs evidence for:

- role-profile validity
- scale interpretation
- scoring reliability
- rater agreement where applicable
- evidence recency policy
- opportunity-to-demonstrate fairness
- resource relevance
- learning impact
- ranking robustness
- governance and appeal

## Human oversight

A reviewer remains responsible for confirming the role profile, challenging evidence, interpreting unknown or weak evidence, selecting development actions, and deciding whether a matched resource is appropriate.

No output should automatically affect hiring, pay, promotion, discipline, or termination.
