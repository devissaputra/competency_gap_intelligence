# Research protocol

## Project

Competency Gap Intelligence

## Research questions

1. How can role requirements and demonstrated competency evidence be represented on a declared, auditable scale?
2. How should missing, stale, or low-confidence evidence affect gap analysis?
3. Which confirmed competency gaps should be prioritized under alternative role-importance assumptions?
4. How should prerequisite competencies change development sequencing?
5. Which learning resources match the learner's current level, target level, and prerequisite state?
6. How stable is the resulting priority order when business importance assumptions change?

## Current baseline

The current implementation separates five stages:

1. role requirement definition
2. competency evidence aggregation
3. evidence-aware gap classification
4. prerequisite-aware sequencing
5. explainable resource matching

The system does not infer proficiency from behavior.

It operates only on declared role requirements and declared competency evidence.

## Declared proficiency scale

Every analysis uses a scale with:

- name
- minimum
- maximum

Targets, observed levels, resource entry levels, and resource target levels are validated against that scale.

The code does not assume that all competency frameworks use a 0–5 scale.

A production adapter should preserve the source framework's level meanings and anchors.

## Role requirements

A role requirement can include:

- target level
- importance
- competency framework/source
- rationale

Importance is allowed to affect the order of **confirmed** gaps.

Importance is not allowed to turn missing or weak evidence into a confident gap.

## Evidence model

Each evidence record can include:

- competency
- observed level
- source
- evidence type
- confidence
- observation date
- assessor

Multiple records for the same competency are aggregated with a transparent confidence-weighted mean.

This is a simple baseline, not a validated psychometric model.

Future empirical work should compare aggregation approaches and test agreement with external criteria.

## Gap states

The current gap engine distinguishes:

- `gap`
- `met`
- `exceeds_target`
- `unknown_evidence`
- `insufficient_evidence`

The critical design rule is:

> missing evidence is not proficiency zero.

Unknown evidence produces an assessment need.

Low-confidence or stale evidence produces a review need.

Only sufficiently supported gaps receive a numeric development priority.

## Priority

For a confirmed gap:

`priority = gap × importance`

This is deliberately simple and inspectable.

It is not presented as a universal utility function.

The repository includes ranking-sensitivity analysis so alternative importance assumptions can be compared directly.

## Prerequisites

Competency dependencies are represented as a directed acyclic graph.

The implementation:

- rejects unknown competency names
- rejects self-dependencies
- rejects cycles
- identifies unresolved prerequisite blockers
- sequences prerequisite competencies before dependent gaps

A large downstream gap therefore does not automatically jump ahead of a missing foundation.

## Resource matching

A resource is represented with:

- competency
- entry level
- target level
- effort
- modality
- competency prerequisites

A resource can be matched only when:

- the competency has a confirmed gap
- the current level meets the resource entry level
- the resource advances beyond the current level
- declared resource prerequisites are already met

Candidates are ordered transparently by:

1. whether they reach the role target
2. how much of the gap they cover
3. lower effort
4. title as a deterministic tie-breaker

There is no hidden recommendation model.

## Development path

The plan distinguishes:

- collect evidence
- review evidence
- develop
- no development required

This is intentionally different from a simple sorted list of deficits.

A competency with uncertain evidence should not be prescribed training merely because its role target is high.

## Ranking sensitivity

`ranking_sensitivity()` compares confirmed-gap order under alternative importance-weight scenarios.

The output reports:

- ranking per scenario
- best rank
- worst rank
- whether a skill's rank is stable across scenarios

A priority that changes sharply under reasonable importance assumptions should be treated as a planning choice rather than an objective fact.

## Validation study

A credible empirical study should evaluate separate questions:

### Role-profile validity

Do independent job experts agree on:

- which competencies belong in the role
- required levels
- importance
- prerequisites

### Evidence validity

Do proficiency judgments agree with:

- work samples
- structured assessments
- validated rubrics
- independent reviewers
- later job performance where ethically and methodologically appropriate

### Reliability

Where human scoring is used, evaluate rater agreement and rubric consistency.

### Recommendation relevance

Do matched resources:

- start at an appropriate level
- actually target the named competency
- respect prerequisites
- produce measurable improvement on independent evidence

### Development impact

A learning resource should not be judged only by completion.

Measure whether credible follow-up evidence shows change in the targeted competency.

## Threats to validity

Major threats include:

- poorly defined competencies
- incompatible proficiency scales
- stale role profiles
- low-quality evidence
- self-report inflation or deflation
- manager-rating bias
- opportunity-to-demonstrate bias
- halo effects
- arbitrary importance weights
- incomplete prerequisite graphs
- resource metadata that overstates learning outcomes
- assuming training is always the correct response to a gap
- using a role framework outside the context for which it was designed

The output should be interpreted as a development hypothesis with visible evidence, not as an objective measure of a person's worth or performance.
