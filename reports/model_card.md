# Analytic system card

## System

Competency Gap Intelligence

## Purpose

Skill gap scoring and resource planning baseline for workplace capability development.

## Current maturity

Working research prototype. The bundled example checks the software path with synthetic inputs. It does not establish validity for real learners, instructors, courses, or workplaces.

## Inputs

See `../data/README.md` for the current synthetic schema and the documentation expected before real data are connected.

## Outputs

The current code produces a ranked set of competency gaps and an optional resource plan. These outputs are research signals and should be interpreted with the educational context that produced them.

## Evidence needed before real use

Compare gap scores with independent evidence and expert judgments. Evaluate ranking stability when importance weights or observed levels change, then test whether recommended resources improve the targeted competency.

## Main limitation

A numerical gap is only as credible as the competency framework and evidence behind it. The current code does not infer skills from employee behavior and should not be used for performance decisions.

## Human oversight

A person must review any output before it can affect a learner, instructor, applicant, or employee.
