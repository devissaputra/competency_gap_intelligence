import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from competency_gap_intelligence.core import (
    aggregate_evidence,
    build_development_plan,
    ranking_sensitivity,
)


SCALE = {
    "name": "Synthetic workplace proficiency scale",
    "minimum": 0,
    "maximum": 5,
}

REQUIREMENTS = {
    "data_literacy": {
        "target": 4,
        "importance": 1.3,
        "framework": "synthetic role profile",
        "rationale": "Required to interpret operational and learning data.",
    },
    "statistics": {
        "target": 3,
        "importance": 1.4,
        "framework": "synthetic role profile",
        "rationale": "Required before advanced learning-analytics work.",
    },
    "learning_analytics": {
        "target": 4,
        "importance": 1.5,
        "framework": "synthetic role profile",
        "rationale": "Core responsibility for evidence-informed learning decisions.",
    },
    "instructional_design": {
        "target": 4,
        "importance": 1.2,
        "framework": "synthetic role profile",
        "rationale": "Needed to translate findings into learning interventions.",
    },
    "facilitation": {
        "target": 3,
        "importance": 0.8,
        "framework": "synthetic role profile",
        "rationale": "Needed for workshops and stakeholder sessions.",
    },
    "stakeholder_communication": {
        "target": 4,
        "importance": 1.0,
        "framework": "synthetic role profile",
        "rationale": "Needed to explain findings to non-technical stakeholders.",
    },
    "python": {
        "target": 3,
        "importance": 1.1,
        "framework": "synthetic role profile",
        "rationale": "Needed for reproducible analysis workflows.",
    },
}

EVIDENCE = [
    {
        "skill": "data_literacy",
        "level": 3.0,
        "source": "work sample",
        "confidence": 0.90,
        "observed_on": "2026-09-10",
        "evidence_type": "work_sample",
        "assessor": "review panel",
    },
    {
        "skill": "data_literacy",
        "level": 3.5,
        "source": "structured assessment",
        "confidence": 0.85,
        "observed_on": "2026-09-14",
        "evidence_type": "assessment",
        "assessor": "assessment rubric",
    },
    {
        "skill": "statistics",
        "level": 2.0,
        "source": "structured assessment",
        "confidence": 0.92,
        "observed_on": "2026-09-12",
        "evidence_type": "assessment",
        "assessor": "assessment rubric",
    },
    {
        "skill": "learning_analytics",
        "level": 2.5,
        "source": "portfolio review",
        "confidence": 0.82,
        "observed_on": "2026-09-16",
        "evidence_type": "portfolio",
        "assessor": "review panel",
    },
    {
        "skill": "instructional_design",
        "level": 4.4,
        "source": "portfolio review",
        "confidence": 0.95,
        "observed_on": "2026-09-18",
        "evidence_type": "portfolio",
        "assessor": "review panel",
    },
    {
        "skill": "stakeholder_communication",
        "level": 3.2,
        "source": "single self-rating",
        "confidence": 0.30,
        "observed_on": "2026-09-19",
        "evidence_type": "self_report",
        "assessor": "self",
    },
    {
        "skill": "python",
        "level": 2.7,
        "source": "coding task",
        "confidence": 0.88,
        "observed_on": "2024-09-01",
        "evidence_type": "work_sample",
        "assessor": "technical reviewer",
    },
]

PREREQUISITES = {
    "learning_analytics": ["statistics"],
}

RESOURCES = [
    {
        "id": "statistics-foundations",
        "title": "Statistics Foundations Practice Lab",
        "competency": "statistics",
        "entry_level": 1,
        "target_level": 3,
        "effort_hours": 12,
        "modality": "project",
        "prerequisites": [],
    },
    {
        "id": "data-literacy-bridge",
        "title": "Applied Data Literacy Bridge",
        "competency": "data_literacy",
        "entry_level": 2,
        "target_level": 4,
        "effort_hours": 8,
        "modality": "self-paced",
        "prerequisites": [],
    },
    {
        "id": "learning-analytics-practice",
        "title": "Learning Analytics Evidence Project",
        "competency": "learning_analytics",
        "entry_level": 2,
        "target_level": 4,
        "effort_hours": 18,
        "modality": "project",
        "prerequisites": ["statistics"],
    },
    {
        "id": "learning-analytics-intro",
        "title": "Learning Analytics Diagnostic Workshop",
        "competency": "learning_analytics",
        "entry_level": 1,
        "target_level": 3,
        "effort_hours": 6,
        "modality": "workshop",
        "prerequisites": [],
    },
    {
        "id": "python-applied-analysis",
        "title": "Python for Reproducible Analysis",
        "competency": "python",
        "entry_level": 2,
        "target_level": 3,
        "effort_hours": 10,
        "modality": "project",
        "prerequisites": [],
    },
]

evidence = aggregate_evidence(
    EVIDENCE,
    scale=SCALE,
    as_of="2026-09-24",
    stale_after_days=365,
)

plan = build_development_plan(
    REQUIREMENTS,
    evidence,
    RESOURCES,
    prerequisites=PREREQUISITES,
    scale=SCALE,
    minimum_confidence=0.50,
)

print("Competency evidence and development-path demo")
print("Scale:", plan["scale"])
print()

for row in plan["analysis"]:
    print(
        row["skill"],
        {
            "status": row["status"],
            "target": row["target"],
            "current": None if row["current"] is None else round(row["current"], 2),
            "gap": None if row["gap"] is None else round(row["gap"], 2),
            "priority": None if row["priority"] is None else round(row["priority"], 2),
            "confidence": None if row["confidence"] is None else round(row["confidence"], 2),
            "flags": row["review_flags"],
        },
    )

print("\nDevelopment sequence:")
for index, item in enumerate(plan["items"], start=1):
    print(
        index,
        item["skill"],
        {
            "action": item["action"],
            "blockers": item["blockers"],
            "resources": [resource["id"] for resource in item["resources"]],
            "reason": item["rationale"],
        },
    )

print("\nAssessment/review needed:", plan["assessment_needed"])

sensitivity = ranking_sensitivity(
    REQUIREMENTS,
    evidence,
    {
        "role_profile": {
            skill: spec["importance"]
            for skill, spec in REQUIREMENTS.items()
        },
        "analytics_critical": {
            "data_literacy": 1.5,
            "statistics": 1.8,
            "learning_analytics": 2.0,
            "instructional_design": 0.9,
            "facilitation": 0.6,
            "stakeholder_communication": 0.8,
            "python": 1.4,
        },
        "delivery_critical": {
            "data_literacy": 0.8,
            "statistics": 0.8,
            "learning_analytics": 1.0,
            "instructional_design": 1.8,
            "facilitation": 1.6,
            "stakeholder_communication": 1.5,
            "python": 0.7,
        },
    },
    scale=SCALE,
)

print("\nConfirmed-gap ranking sensitivity:")
for name, ranking in sensitivity["rankings"].items():
    print(name, ranking)

print(
    "\nNote: all role requirements, evidence records, confidence values, "
    "prerequisites, and learning resources are synthetic. "
    "Unknown or weak evidence is not converted into a zero proficiency score."
)
