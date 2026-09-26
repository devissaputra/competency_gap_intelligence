# Calculation guide

## Question and evidence

Which evidenced skill gaps should be addressed first?

Supplied role targets, dated competency evidence, prerequisites and resource metadata.

**Status:** SYNTHETIC / RULE-BASED PROTOTYPE | no educational validity claim.

## Design

Confidence-weight evidence; retain unknown/stale status; prioritize confirmed gaps and check prerequisites.

## Calculation and interpretation

`Observed level = sum(confidence×level)/sum(confidence); priority = positive gap×importance.`

Missing evidence is not a zero skill level. Levels and confidence must share a justified scale. Weighting summarizes supplied judgments; it does not validate the underlying assessment or resource effectiveness.

## Evidence table

Worked example — illustrative, not a measured research result. Full precision below is for traceability, not a claim of measurement precision.

| Quantity | Value | Unit / meaning | JSON path |
|---|---:|---|---|
| weighted level: levels 2,4; weights 1,3 | 3.5 | unitless | `outputs.weighted level: levels 2,4; weights 1,3` |
| gap: target 4 minus level 3.5 | 0.5 | unitless | `outputs.gap: target 4 minus level 3.5` |
| priority: gap .5 times importance 2 | 1.0 | unitless | `outputs.priority: gap .5 times importance 2` |

Source: [results/review_examples.json](results/review_examples.json). Values resolve directly from this file when figures are regenerated.

This competency-planning prototype compares role requirements with dated, confidence-labeled evidence and keeps missing or stale evidence visible. Only sufficiently supported gaps are ranked, after which prerequisite constraints shape development sequences and resource matches. The calculations are auditable decision support; they do not turn subjective competency ratings into validated measures.

## Verification performed in this review

32 existing unittest checks passed. The bundled demonstration executed successfully in this review.

The figure-generation check verifies agreement between the selected source values and SVGs. It does not validate the raw dataset, fitted model, identification assumptions, or external generalization.

```bash
python scripts/build_review_figures.py
python scripts/build_review_figures.py --check
```

For the explicitly illustrative example:

```bash
python scripts/review_examples.py
```

## Implementation map

Follow these functions to inspect each transformation. Validation helpers and private functions remain visible in the linked modules.

| Function | Purpose / documented behavior |
|---|---|
| [`validate_scale`](src/competency_gap_intelligence/core.py#L28) | Validate a declared proficiency scale. |
| [`validate_requirements`](src/competency_gap_intelligence/core.py#L74) | Validate role requirements and return a normalized requirement mapping. |
| [`aggregate_evidence`](src/competency_gap_intelligence/core.py#L134) | Aggregate competency evidence without turning missing evidence into zero. |
| [`competency_gaps`](src/competency_gap_intelligence/core.py#L309) | Analyze competency status without conflating missing evidence with zero. |
| [`validate_prerequisites`](src/competency_gap_intelligence/core.py#L413) | Validate a prerequisite graph and reject cycles. |
| [`prerequisite_blockers`](src/competency_gap_intelligence/core.py#L466) | Return unmet or unverified prerequisites for each competency. |
| [`development_sequence`](src/competency_gap_intelligence/core.py#L487) | Topologically order competencies that need development or assessment. |
| [`validate_resources`](src/competency_gap_intelligence/core.py#L539) | Validate structured learning resources. |
| [`match_resources`](src/competency_gap_intelligence/core.py#L636) | Match resources transparently to confirmed competency gaps. |
| [`build_development_plan`](src/competency_gap_intelligence/core.py#L724) | Build an explainable prerequisite-aware development and assessment plan. |
| [`development_plan`](src/competency_gap_intelligence/core.py#L805) | Backward-friendly wrapper for structured development planning. |
| [`ranking_sensitivity`](src/competency_gap_intelligence/core.py#L851) | Compare confirmed-gap rankings across alternative importance weights. |
| [`visit`](src/competency_gap_intelligence/core.py#L449) | Inspect the explicit implementation and its callers. |
| [`ordering_key`](src/competency_gap_intelligence/core.py#L501) | Inspect the explicit implementation and its callers. |

## What remains before a stronger research claim

Missing evidence is not a zero skill level. Levels and confidence must share a justified scale. Weighting summarizes supplied judgments; it does not validate the underlying assessment or resource effectiveness. A successful software test is not validation of a scientific construct. New experiments should state their split unit, comparator, outcome, uncertainty procedure and failure criteria before examining final test results.
