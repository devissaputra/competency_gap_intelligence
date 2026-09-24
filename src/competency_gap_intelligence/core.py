def competency_gaps(required, observed, importance=None):
    """Rank non-negative competency gaps by gap size and optional importance."""
    importance = importance or {skill: 1.0 for skill in required}
    rows = []
    for skill, target in required.items():
        if target < 0:
            raise ValueError("required competency levels must be non-negative")
        current = observed.get(skill, 0.0)
        if current < 0:
            raise ValueError("observed competency levels must be non-negative")
        weight = importance.get(skill, 1.0)
        if weight < 0:
            raise ValueError("importance weights must be non-negative")
        gap = max(0.0, target - current)
        rows.append(
            {
                "skill": skill,
                "target": target,
                "current": current,
                "gap": gap,
                "priority": gap * weight,
            }
        )
    return sorted(rows, key=lambda row: (-row["priority"], row["skill"]))


def development_plan(required, observed, resources, importance=None):
    """Attach up to three candidate resources to each positive competency gap."""
    gaps = competency_gaps(required, observed, importance)
    return [
        {**gap, "resources": list(resources.get(gap["skill"], []))[:3]}
        for gap in gaps
        if gap["gap"] > 0
    ]
