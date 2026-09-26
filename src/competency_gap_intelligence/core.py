# Calculation reading guide: ../CALCULATIONS.md (repository root).
# Observed level = sum(confidence×level)/sum(confidence); priority = positive gap×importance.
# Missing evidence is not a zero skill level. Levels and confidence must share a justified scale. Weighting summarizes supplied judgments; it does not validate the underlying assessment or resource effectiveness.

import math
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from numbers import Real


DEFAULT_SCALE = {
    "name": "declared proficiency scale",
    "minimum": 0.0,
    "maximum": 5.0,
}


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def validate_scale(scale=None):
    """Validate a declared proficiency scale."""
    scale = dict(DEFAULT_SCALE if scale is None else scale)
    required_keys = {"name", "minimum", "maximum"}
    if set(scale) != required_keys:
        raise ValueError(
            "scale must contain exactly name, minimum, and maximum"
        )

    if not isinstance(scale["name"], str) or not scale["name"].strip():
        raise ValueError("scale name must be a non-empty string")

    minimum = _finite_number(scale["minimum"], "scale minimum")
    maximum = _finite_number(scale["maximum"], "scale maximum")
    if minimum >= maximum:
        raise ValueError("scale minimum must be lower than maximum")

    return {
        "name": scale["name"].strip(),
        "minimum": minimum,
        "maximum": maximum,
    }


def _validate_level(value, name, scale):
    value = _finite_number(value, name)
    if not scale["minimum"] <= value <= scale["maximum"]:
        raise ValueError(
            f"{name} must be between {scale['minimum']} and {scale['maximum']}"
        )
    return value


def _parse_date(value, name):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc


def validate_requirements(requirements, *, scale=None, importance=None):
    """Validate role requirements and return a normalized requirement mapping."""
    scale = validate_scale(scale)
    if not isinstance(requirements, Mapping) or not requirements:
        raise ValueError("requirements must be a non-empty mapping")

    importance = {} if importance is None else dict(importance)
    unknown_importance = set(importance) - set(requirements)
    if unknown_importance:
        raise ValueError(
            f"importance contains unknown competencies: {sorted(unknown_importance)}"
        )

    normalized = {}
    for skill, value in requirements.items():
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("competency names must be non-empty strings")
        skill = skill.strip()

        if isinstance(value, Mapping):
            if "target" not in value:
                raise ValueError(f"requirement {skill} must define target")
            target = _validate_level(
                value["target"],
                f"{skill} target",
                scale,
            )
            weight = value.get("importance", importance.get(skill, 1.0))
            framework = value.get("framework")
            rationale = value.get("rationale")
        else:
            target = _validate_level(value, f"{skill} target", scale)
            weight = importance.get(skill, 1.0)
            framework = None
            rationale = None

        weight = _finite_number(weight, f"{skill} importance")
        if weight < 0:
            raise ValueError("importance weights must be non-negative")

        if framework is not None and (
            not isinstance(framework, str) or not framework.strip()
        ):
            raise ValueError("framework must be a non-empty string when supplied")

        if rationale is not None and (
            not isinstance(rationale, str) or not rationale.strip()
        ):
            raise ValueError("rationale must be a non-empty string when supplied")

        normalized[skill] = {
            "target": target,
            "importance": weight,
            "framework": framework.strip() if framework else None,
            "rationale": rationale.strip() if rationale else None,
        }

    return normalized


def aggregate_evidence(
    evidence_records,
    *,
    scale=None,
    as_of=None,
    stale_after_days=365,
):
    """Aggregate competency evidence without turning missing evidence into zero."""
    scale = validate_scale(scale)
    if not isinstance(evidence_records, Sequence):
        raise ValueError("evidence_records must be a sequence")
    if isinstance(stale_after_days, bool) or not isinstance(stale_after_days, int):
        raise ValueError("stale_after_days must be an integer")
    if stale_after_days <= 0:
        raise ValueError("stale_after_days must be positive")

    as_of = date.today() if as_of is None else _parse_date(as_of, "as_of")
    grouped = defaultdict(list)

    for index, record in enumerate(evidence_records):
        if not isinstance(record, Mapping):
            raise ValueError("each evidence record must be a mapping")

        for field in ("skill", "level", "source", "confidence", "observed_on"):
            if field not in record:
                raise ValueError(f"evidence record {index} is missing {field}")

        skill = record["skill"]
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("evidence skill must be a non-empty string")
        skill = skill.strip()

        source = record["source"]
        if not isinstance(source, str) or not source.strip():
            raise ValueError("evidence source must be a non-empty string")

        evidence_type = record.get("evidence_type", "unspecified")
        if not isinstance(evidence_type, str) or not evidence_type.strip():
            raise ValueError("evidence_type must be a non-empty string")

        assessor = record.get("assessor")
        if assessor is not None and (
            not isinstance(assessor, str) or not assessor.strip()
        ):
            raise ValueError("assessor must be a non-empty string when supplied")

        level = _validate_level(
            record["level"],
            f"{skill} evidence level",
            scale,
        )
        confidence = _validate_level(
            record["confidence"],
            f"{skill} evidence confidence",
            {"minimum": 0.0, "maximum": 1.0, "name": "confidence"},
        )
        observed_on = _parse_date(record["observed_on"], "observed_on")
        if observed_on > as_of:
            raise ValueError("evidence date cannot be after as_of")

        grouped[skill].append(
            {
                "level": level,
                "source": source.strip(),
                "confidence": confidence,
                "observed_on": observed_on,
                "evidence_type": evidence_type.strip(),
                "assessor": assessor.strip() if assessor else None,
            }
        )

    summaries = {}
    for skill, records in grouped.items():
        positive_confidence = [
            record for record in records if record["confidence"] > 0
        ]

        if positive_confidence:
            confidence_sum = sum(
                record["confidence"] for record in positive_confidence
            )
            level = sum(
                record["level"] * record["confidence"]
                for record in positive_confidence
            ) / confidence_sum
        else:
            level = None

        latest = max(record["observed_on"] for record in records)
        age_days = (as_of - latest).days
        mean_confidence = sum(
            record["confidence"] for record in records
        ) / len(records)

        summaries[skill] = {
            "level": level,
            "evidence_count": len(records),
            "mean_confidence": mean_confidence,
            "latest_observed_on": latest.isoformat(),
            "age_days": age_days,
            "stale": age_days > stale_after_days,
            "sources": sorted({record["source"] for record in records}),
            "evidence_types": sorted(
                {record["evidence_type"] for record in records}
            ),
            "assessors": sorted(
                {
                    record["assessor"]
                    for record in records
                    if record["assessor"] is not None
                }
            ),
        }

    return summaries


def _normalize_observed(observed, *, scale):
    """Normalize direct observed levels or aggregated evidence summaries."""
    if not isinstance(observed, Mapping):
        raise ValueError("observed must be a mapping")

    normalized = {}
    for skill, value in observed.items():
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("competency names must be non-empty strings")
        skill = skill.strip()

        if isinstance(value, Mapping):
            level = value.get("level")
            if level is not None:
                level = _validate_level(
                    level,
                    f"{skill} observed level",
                    scale,
                )
            confidence = value.get("mean_confidence", value.get("confidence", 1.0))
            confidence = _validate_level(
                confidence,
                f"{skill} confidence",
                {"minimum": 0.0, "maximum": 1.0, "name": "confidence"},
            )
            stale = bool(value.get("stale", False))
            evidence_count = value.get("evidence_count", 1)
            if (
                isinstance(evidence_count, bool)
                or not isinstance(evidence_count, int)
                or evidence_count < 0
            ):
                raise ValueError("evidence_count must be a non-negative integer")
            normalized[skill] = {
                "level": level,
                "confidence": confidence,
                "stale": stale,
                "evidence_count": evidence_count,
                "sources": list(value.get("sources", [])),
                "latest_observed_on": value.get("latest_observed_on"),
            }
        else:
            normalized[skill] = {
                "level": _validate_level(
                    value,
                    f"{skill} observed level",
                    scale,
                ),
                "confidence": 1.0,
                "stale": False,
                "evidence_count": 1,
                "sources": ["direct input"],
                "latest_observed_on": None,
            }

    return normalized


def competency_gaps(
    required,
    observed,
    importance=None,
    *,
    scale=None,
    minimum_confidence=0.5,
):
    """Analyze competency status without conflating missing evidence with zero."""
    scale = validate_scale(scale)
    requirements = validate_requirements(
        required,
        scale=scale,
        importance=importance,
    )
    observed = _normalize_observed(observed, scale=scale)

    minimum_confidence = _validate_level(
        minimum_confidence,
        "minimum_confidence",
        {"minimum": 0.0, "maximum": 1.0, "name": "confidence"},
    )

    rows = []
    for skill, requirement in requirements.items():
        evidence = observed.get(skill)

        if evidence is None or evidence["level"] is None:
            status = "unknown_evidence"
            current = None
            gap = None
            priority = None
            flags = ["assessment_needed"]
            confidence = None if evidence is None else evidence["confidence"]
        else:
            current = evidence["level"]
            confidence = evidence["confidence"]
            gap_value = requirement["target"] - current
            flags = []

            if evidence["stale"]:
                flags.append("stale_evidence")
            if confidence < minimum_confidence:
                flags.append("low_confidence_evidence")

            if flags:
                status = "insufficient_evidence"
                gap = max(0.0, gap_value)
                priority = None
                flags.append("review_before_ranking")
            elif gap_value > 0:
                status = "gap"
                gap = gap_value
                priority = gap * requirement["importance"]
            elif gap_value < 0:
                status = "exceeds_target"
                gap = 0.0
                priority = 0.0
            else:
                status = "met"
                gap = 0.0
                priority = 0.0

        rows.append(
            {
                "skill": skill,
                "target": requirement["target"],
                "current": current,
                "status": status,
                "gap": gap,
                "importance": requirement["importance"],
                "priority": priority,
                "confidence": confidence,
                "framework": requirement["framework"],
                "rationale": requirement["rationale"],
                "evidence_count": (
                    0 if evidence is None else evidence["evidence_count"]
                ),
                "sources": [] if evidence is None else evidence["sources"],
                "latest_observed_on": (
                    None if evidence is None else evidence["latest_observed_on"]
                ),
                "review_flags": flags,
            }
        )

    status_order = {
        "gap": 0,
        "insufficient_evidence": 1,
        "unknown_evidence": 2,
        "met": 3,
        "exceeds_target": 4,
    }

    return sorted(
        rows,
        key=lambda row: (
            status_order[row["status"]],
            -(row["priority"] or 0.0),
            row["skill"],
        ),
    )


def validate_prerequisites(prerequisites, competencies):
    """Validate a prerequisite graph and reject cycles."""
    if prerequisites is None:
        return {skill: [] for skill in competencies}
    if not isinstance(prerequisites, Mapping):
        raise ValueError("prerequisites must be a mapping")

    competencies = set(competencies)
    unknown_keys = set(prerequisites) - competencies
    if unknown_keys:
        raise ValueError(
            f"prerequisites contains unknown competencies: {sorted(unknown_keys)}"
        )

    graph = {skill: [] for skill in competencies}
    for skill, parents in prerequisites.items():
        if not isinstance(parents, Sequence) or isinstance(parents, (str, bytes)):
            raise ValueError("each prerequisite list must be a sequence")
        cleaned = []
        for parent in parents:
            if not isinstance(parent, str) or not parent.strip():
                raise ValueError("prerequisite names must be non-empty strings")
            parent = parent.strip()
            if parent not in competencies:
                raise ValueError(
                    f"prerequisite {parent} for {skill} is not a known competency"
                )
            if parent == skill:
                raise ValueError("a competency cannot depend on itself")
            if parent not in cleaned:
                cleaned.append(parent)
        graph[skill] = cleaned

    visiting = set()
    visited = set()

    def visit(node):
        if node in visiting:
            raise ValueError("prerequisite graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for parent in graph[node]:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for skill in competencies:
        visit(skill)

    return graph


def prerequisite_blockers(analysis, prerequisites):
    """Return unmet or unverified prerequisites for each competency."""
    by_skill = {row["skill"]: row for row in analysis}
    graph = validate_prerequisites(prerequisites, by_skill)

    blockers = {}
    for skill, parents in graph.items():
        current = []
        for parent in parents:
            row = by_skill[parent]
            if row["status"] not in ("met", "exceeds_target"):
                current.append(
                    {
                        "skill": parent,
                        "status": row["status"],
                    }
                )
        blockers[skill] = current
    return blockers


def development_sequence(analysis, prerequisites=None):
    """Topologically order competencies that need development or assessment."""
    by_skill = {row["skill"]: row for row in analysis}
    graph = validate_prerequisites(prerequisites, by_skill)

    included = set(by_skill)

    indegree = {skill: 0 for skill in included}
    children = {skill: [] for skill in included}
    for skill in included:
        for parent in graph[skill]:
            indegree[skill] += 1
            children[parent].append(skill)

    def ordering_key(skill):
        status_rank = {
            "gap": 0,
            "unknown_evidence": 1,
            "insufficient_evidence": 2,
            "met": 3,
            "exceeds_target": 4,
        }
        return (
            status_rank[by_skill[skill]["status"]],
            -(by_skill[skill]["priority"] or 0.0),
            skill,
        )

    available = sorted(
        (
            skill
            for skill, degree in indegree.items()
            if degree == 0
        ),
        key=ordering_key,
    )

    order = []
    while available:
        skill = available.pop(0)
        order.append(skill)
        for child in children[skill]:
            indegree[child] -= 1
            if indegree[child] == 0:
                available.append(child)
        available.sort(key=ordering_key)

    if len(order) != len(included):
        raise ValueError("could not resolve prerequisite sequence")
    return order


def validate_resources(resources, *, scale=None, competencies=None):
    """Validate structured learning resources."""
    scale = validate_scale(scale)
    if not isinstance(resources, Sequence):
        raise ValueError("resources must be a sequence")

    competencies = None if competencies is None else set(competencies)
    ids = set()
    normalized = []

    for index, resource in enumerate(resources):
        if not isinstance(resource, Mapping):
            raise ValueError("each resource must be a mapping")

        for field in (
            "id",
            "title",
            "competency",
            "entry_level",
            "target_level",
            "effort_hours",
            "modality",
        ):
            if field not in resource:
                raise ValueError(f"resource {index} is missing {field}")

        resource_id = resource["id"]
        title = resource["title"]
        competency = resource["competency"]
        modality = resource["modality"]

        for value, name in (
            (resource_id, "resource id"),
            (title, "resource title"),
            (competency, "resource competency"),
            (modality, "resource modality"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        resource_id = resource_id.strip()
        if resource_id in ids:
            raise ValueError(f"duplicate resource id: {resource_id}")
        ids.add(resource_id)

        competency = competency.strip()
        if competencies is not None and competency not in competencies:
            raise ValueError(
                f"resource competency {competency} is not in the competency framework"
            )

        entry_level = _validate_level(
            resource["entry_level"],
            f"{resource_id} entry_level",
            scale,
        )
        target_level = _validate_level(
            resource["target_level"],
            f"{resource_id} target_level",
            scale,
        )
        if target_level <= entry_level:
            raise ValueError("resource target_level must exceed entry_level")

        effort_hours = _finite_number(
            resource["effort_hours"],
            f"{resource_id} effort_hours",
        )
        if effort_hours <= 0:
            raise ValueError("effort_hours must be positive")

        resource_prerequisites = resource.get("prerequisites", [])
        if (
            not isinstance(resource_prerequisites, Sequence)
            or isinstance(resource_prerequisites, (str, bytes))
        ):
            raise ValueError("resource prerequisites must be a sequence")

        normalized.append(
            {
                "id": resource_id,
                "title": title.strip(),
                "competency": competency,
                "entry_level": entry_level,
                "target_level": target_level,
                "effort_hours": effort_hours,
                "modality": modality.strip(),
                "prerequisites": [
                    prerequisite.strip()
                    for prerequisite in resource_prerequisites
                ],
            }
        )

    return normalized


def match_resources(
    analysis,
    resources,
    *,
    scale=None,
    max_per_skill=3,
):
    """Match resources transparently to confirmed competency gaps."""
    if (
        isinstance(max_per_skill, bool)
        or not isinstance(max_per_skill, int)
        or max_per_skill <= 0
    ):
        raise ValueError("max_per_skill must be a positive integer")

    by_skill = {row["skill"]: row for row in analysis}
    resources = validate_resources(
        resources,
        scale=scale,
        competencies=by_skill,
    )

    matches = {}
    for skill, row in by_skill.items():
        if row["status"] != "gap":
            matches[skill] = []
            continue

        current = row["current"]
        target = row["target"]
        candidates = []

        for resource in resources:
            if resource["competency"] != skill:
                continue

            if current < resource["entry_level"]:
                continue
            if resource["target_level"] <= current:
                continue

            resource_blockers = []
            for prerequisite in resource["prerequisites"]:
                prerequisite_row = by_skill.get(prerequisite)
                if prerequisite_row is None:
                    raise ValueError(
                        f"resource prerequisite {prerequisite} is not in the competency framework"
                    )
                if prerequisite_row["status"] not in ("met", "exceeds_target"):
                    resource_blockers.append(
                        {
                            "skill": prerequisite,
                            "status": prerequisite_row["status"],
                        }
                    )

            if resource_blockers:
                continue

            coverage = min(target, resource["target_level"]) - current
            candidates.append(
                {
                    **resource,
                    "coverage": coverage,
                    "reaches_role_target": resource["target_level"] >= target,
                    "resource_blockers": resource_blockers,
                    "rationale": (
                        f"Current level {current:.2f} meets entry level "
                        f"{resource['entry_level']:.2f}; resource targets "
                        f"{resource['target_level']:.2f} toward role target {target:.2f}; "
                        "declared resource prerequisites are currently met."
                    ),
                }
            )

        candidates.sort(
            key=lambda resource: (
                not resource["reaches_role_target"],
                -resource["coverage"],
                resource["effort_hours"],
                resource["title"],
            )
        )
        matches[skill] = candidates[:max_per_skill]

    return matches


def build_development_plan(
    required,
    observed,
    resources,
    *,
    importance=None,
    prerequisites=None,
    scale=None,
    minimum_confidence=0.5,
):
    """Build an explainable prerequisite-aware development and assessment plan."""
    scale = validate_scale(scale)
    analysis = competency_gaps(
        required,
        observed,
        importance,
        scale=scale,
        minimum_confidence=minimum_confidence,
    )
    by_skill = {row["skill"]: row for row in analysis}
    graph = validate_prerequisites(prerequisites, by_skill)
    blockers = prerequisite_blockers(analysis, graph)
    matches = match_resources(
        analysis,
        resources,
        scale=scale,
    )
    sequence = development_sequence(analysis, graph)

    items = []
    for skill in sequence:
        row = by_skill[skill]

        if row["status"] in ("met", "exceeds_target"):
            action = "no_development_required"
            rationale = "Prerequisite already meets or exceeds its role target."
        elif row["status"] == "unknown_evidence":
            action = "collect_evidence"
            rationale = (
                "No defensible proficiency evidence is available; assess before prescribing training."
            )
        elif row["status"] == "insufficient_evidence":
            action = "review_evidence"
            rationale = (
                "Evidence exists but is stale or below the confidence threshold; verify before ranking."
            )
        else:
            action = "develop"
            if blockers[skill]:
                rationale = "Address prerequisite blockers before this competency."
            else:
                rationale = "Confirmed competency gap with sufficient evidence."

        items.append(
            {
                "skill": skill,
                "action": action,
                "status": row["status"],
                "target": row["target"],
                "current": row["current"],
                "gap": row["gap"],
                "priority": row["priority"],
                "blockers": blockers[skill],
                "resources": matches[skill],
                "rationale": rationale,
            }
        )

    return {
        "scale": scale,
        "analysis": analysis,
        "sequence": sequence,
        "items": items,
        "assessment_needed": [
            row["skill"]
            for row in analysis
            if row["status"] in ("unknown_evidence", "insufficient_evidence")
        ],
    }


def development_plan(
    required,
    observed,
    resources,
    importance=None,
    *,
    prerequisites=None,
    scale=None,
    minimum_confidence=0.5,
):
    """Backward-friendly wrapper for structured development planning.

    The previous prototype accepted a mapping of skill -> resource names.
    That format is converted into structured resources with broad level coverage.
    """
    scale = validate_scale(scale)

    if isinstance(resources, Mapping):
        structured = []
        for skill, titles in resources.items():
            for index, title in enumerate(titles):
                structured.append(
                    {
                        "id": f"{skill}-{index + 1}",
                        "title": str(title),
                        "competency": skill,
                        "entry_level": scale["minimum"],
                        "target_level": scale["maximum"],
                        "effort_hours": 1.0,
                        "modality": "unspecified",
                        "prerequisites": [],
                    }
                )
        resources = structured

    return build_development_plan(
        required,
        observed,
        resources,
        importance=importance,
        prerequisites=prerequisites,
        scale=scale,
        minimum_confidence=minimum_confidence,
    )


def ranking_sensitivity(
    required,
    observed,
    importance_scenarios,
    *,
    scale=None,
    minimum_confidence=0.5,
):
    """Compare confirmed-gap rankings across alternative importance weights."""
    if not isinstance(importance_scenarios, Mapping) or not importance_scenarios:
        raise ValueError("importance_scenarios must be a non-empty mapping")

    rankings = {}
    for name, weights in importance_scenarios.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("scenario names must be non-empty strings")
        rows = competency_gaps(
            required,
            observed,
            weights,
            scale=scale,
            minimum_confidence=minimum_confidence,
        )
        rankings[name] = [
            row["skill"] for row in rows if row["status"] == "gap"
        ]

    all_skills = sorted(
        {
            skill
            for ranking in rankings.values()
            for skill in ranking
        }
    )
    rank_ranges = {}
    for skill in all_skills:
        positions = []
        for ranking in rankings.values():
            if skill in ranking:
                positions.append(ranking.index(skill) + 1)
        rank_ranges[skill] = {
            "best_rank": min(positions),
            "worst_rank": max(positions),
            "stable_rank": len(set(positions)) == 1,
        }

    return {
        "rankings": rankings,
        "rank_ranges": rank_ranges,
    }
