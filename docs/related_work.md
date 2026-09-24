# Related work and methodological context

Competency Gap Intelligence is an original implementation for transparent competency-evidence review and development planning.

It does not reproduce or redistribute a proprietary competency framework.

## ESCO

The European Skills, Competences, Qualifications and Occupations classification provides a shared European vocabulary connecting occupations with relevant knowledge, skills, and competences.

- About ESCO: https://esco.ec.europa.eu/en/about-esco
- Classification: https://esco.ec.europa.eu/en/classification
- Skills and competences: https://esco.ec.europa.eu/en/classification/skill-main

ESCO is useful context for this repository because it makes relationships between occupations and skills explicit.

The current code does not download or embed ESCO content.

## O*NET

The O*NET Content Model organizes worker and job information including skills, knowledge, abilities, work activities, and occupational requirements.

- O*NET Content Model: https://www.onetcenter.org/content.html
- Competency frameworks: https://www.onetcenter.org/competencyFrameworks.html
- Scales reference: https://www.onetcenter.org/dictionary/31.0/json/scales_reference.html
- Level scale anchors: https://www.onetcenter.org/dictionary/31.0/json/level_scale_anchors.html

O*NET is particularly relevant to the repository's insistence on explicit scales and scale anchors rather than treating an unexplained number such as "4" as universally meaningful.

The current code does not embed O*NET ratings.

## SFIA

SFIA provides a common language for professional skills in digital work and uses seven levels of responsibility.

- About SFIA: https://sfia-online.org/en/about-sfia
- How SFIA works: https://sfia-online.org/en/about-sfia/how-sfia-works
- SFIA 9 framework: https://sfia-online.org/en/the-sfia-framework

SFIA illustrates why competency levels should preserve their source meaning. A level number is meaningful only with the framework's definitions of responsibility, autonomy, influence, complexity, knowledge, and professional practice.

The repository's synthetic 0–5 demo scale is not a substitute for SFIA levels.

## Design relationship

These frameworks provide reference vocabularies and structured level concepts.

This repository focuses on a different layer:

- bringing a role requirement into an explicit local analysis
- attaching observed evidence with provenance
- separating missing evidence from low proficiency
- identifying prerequisite blockers
- matching structured development resources
- testing whether ranking assumptions are stable

## Scope boundary

Implemented:

- declared proficiency scales
- evidence provenance/confidence/age
- confidence-weighted evidence aggregation
- evidence-aware gap states
- importance-weighted priority for confirmed gaps
- prerequisite graph validation
- prerequisite-aware sequencing
- explainable resource matching
- ranking sensitivity

Not implemented:

- automatic ESCO/O*NET/SFIA ingestion
- semantic skill extraction from resumes or work traces
- ontology alignment
- psychometric item-response modeling
- learned recommendation models
- causal estimates of training effectiveness
- employment decision automation
