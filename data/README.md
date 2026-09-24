# Data documentation

## Included data

`sample.csv` contains only synthetic competency-evidence records created for demonstrations and tests.

It is not an employee assessment dataset.

## Why the evidence model matters

A missing competency record does **not** mean proficiency zero.

The current implementation therefore distinguishes:

- confirmed gap
- target met
- target exceeded
- unknown evidence
- insufficient evidence

Unknown and insufficient evidence are routed to assessment/review instead of being silently ranked as development deficits.

## Current synthetic schema

- `person`: synthetic record owner
- `skill`: competency name
- `target`: required role level
- `importance`: declared role importance weight
- `observed_level`: demonstrated level from one evidence source
- `evidence_source`: provenance of the observation
- `evidence_type`: work sample, assessment, portfolio, self-report, or another declared type
- `confidence`: confidence in this evidence record from 0 to 1
- `observed_on`: date the evidence was observed
- `assessor`: declared reviewer or assessment mechanism

## Proficiency scale

The software requires a declared numeric scale with:

- name
- minimum
- maximum

The demo uses a synthetic 0–5 scale only for illustration.

Do not assume that every competency framework uses the same scale.

For example, SFIA uses seven levels of responsibility, while O*NET uses named scales with defined ranges and scale anchors. A production adapter should preserve the source framework's own level semantics rather than merely remapping numbers.

## Requirement provenance

For real use, every role requirement should record:

- competency framework or source
- required level
- importance
- why the competency matters for the role
- date/version of the role profile
- who approved the requirement

Role profiles become stale too.

## Evidence provenance

For each competency observation, record:

- evidence source
- evidence type
- date
- assessor
- scoring rubric
- scale used
- confidence or quality signal
- any moderation process

The current baseline combines multiple observations with a confidence-weighted mean. That is a transparent baseline, not a universal psychometric model.

## Evidence age

The aggregation function can flag evidence older than a declared threshold.

Stale evidence is not automatically discarded or treated as zero. It becomes a review condition.

## Missing and weak evidence

The software does not prescribe development when:

- there is no evidence
- all usable evidence has zero confidence
- evidence falls below the configured confidence threshold
- evidence is marked stale

Instead it recommends collecting or reviewing evidence.

## Prerequisites

Competency prerequisites are represented explicitly as a directed acyclic graph.

A plan can therefore sequence a prerequisite competency before a dependent gap.

Cycles and unknown prerequisite names are rejected.

## Learning resources

Structured resources contain:

- id
- title
- target competency
- entry level
- target level
- effort hours
- modality
- declared prerequisites

A resource is only matched when the current level meets its entry level, it advances the competency, and its declared competency prerequisites are already met.

## Do not commit

Do not commit identifiable employee assessments, confidential performance ratings, manager notes, disability or health information, private work samples, compensation data, disciplinary records, or proprietary competency frameworks that cannot legally be redistributed.

## Real-data card

Before any empirical study, document the competency framework, proficiency scale and anchors, role-profile version, evidence collection process, rater training, inter-rater or scoring reliability where relevant, missingness, evidence recency, known biases, privacy controls, appeal/correction process, and permitted uses.
