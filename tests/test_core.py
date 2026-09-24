import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from competency_gap_intelligence import core


SCALE = {
    "name": "Synthetic 0-5 proficiency scale",
    "minimum": 0,
    "maximum": 5,
}

REQUIRED = {
    "data_literacy": {"target": 4, "importance": 1.4},
    "statistics": {"target": 3, "importance": 1.3},
    "learning_analytics": {"target": 4, "importance": 1.5},
    "instructional_design": {"target": 4, "importance": 1.2},
    "facilitation": {"target": 3, "importance": 0.8},
}

OBSERVED = {
    "data_literacy": {"level": 3.2, "mean_confidence": 0.85},
    "statistics": {"level": 2.0, "mean_confidence": 0.90},
    "learning_analytics": {"level": 2.4, "mean_confidence": 0.80},
    "instructional_design": {"level": 4.3, "mean_confidence": 0.95},
}

RESOURCES = [
    {
        "id": "stats-foundations",
        "title": "Statistics Foundations Lab",
        "competency": "statistics",
        "entry_level": 1,
        "target_level": 3,
        "effort_hours": 12,
        "modality": "project",
        "prerequisites": [],
    },
    {
        "id": "la-practice",
        "title": "Learning Analytics Practice",
        "competency": "learning_analytics",
        "entry_level": 2,
        "target_level": 4,
        "effort_hours": 18,
        "modality": "project",
        "prerequisites": ["statistics"],
    },
    {
        "id": "data-bridge",
        "title": "Data Literacy Bridge",
        "competency": "data_literacy",
        "entry_level": 2,
        "target_level": 4,
        "effort_hours": 8,
        "modality": "self-paced",
        "prerequisites": [],
    },
]

PREREQUISITES = {
    "learning_analytics": ["statistics"],
}


class CoreTests(unittest.TestCase):
    def test_default_scale_validates(self):
        scale = core.validate_scale()
        self.assertLess(scale["minimum"], scale["maximum"])

    def test_invalid_scale_is_rejected(self):
        with self.assertRaises(ValueError):
            core.validate_scale(
                {"name": "bad", "minimum": 5, "maximum": 1}
            )

    def test_requirement_outside_scale_is_rejected(self):
        with self.assertRaises(ValueError):
            core.competency_gaps(
                {"analytics": 6},
                {"analytics": 2},
                scale=SCALE,
            )

    def test_nan_requirement_is_rejected(self):
        with self.assertRaises(ValueError):
            core.competency_gaps(
                {"analytics": math.nan},
                {"analytics": 2},
                scale=SCALE,
            )

    def test_boolean_observed_level_is_rejected(self):
        with self.assertRaises(ValueError):
            core.competency_gaps(
                {"analytics": 4},
                {"analytics": True},
                scale=SCALE,
            )

    def test_missing_evidence_is_not_zero(self):
        rows = core.competency_gaps(
            {"analytics": 4},
            {},
            scale=SCALE,
        )
        self.assertEqual(rows[0]["status"], "unknown_evidence")
        self.assertIsNone(rows[0]["current"])
        self.assertIsNone(rows[0]["gap"])
        self.assertIsNone(rows[0]["priority"])

    def test_confirmed_gap_is_ranked(self):
        rows = core.competency_gaps(
            {"a": 4, "b": 3},
            {"a": 2, "b": 2},
            {"a": 2, "b": 1},
            scale=SCALE,
        )
        self.assertEqual(rows[0]["skill"], "a")
        self.assertEqual(rows[0]["gap"], 2)
        self.assertEqual(rows[0]["priority"], 4)

    def test_met_status(self):
        row = core.competency_gaps(
            {"a": 3},
            {"a": 3},
            scale=SCALE,
        )[0]
        self.assertEqual(row["status"], "met")

    def test_exceeds_target_status(self):
        row = core.competency_gaps(
            {"a": 3},
            {"a": 4},
            scale=SCALE,
        )[0]
        self.assertEqual(row["status"], "exceeds_target")
        self.assertEqual(row["gap"], 0)

    def test_low_confidence_blocks_ranking(self):
        row = core.competency_gaps(
            {"a": 4},
            {"a": {"level": 2, "mean_confidence": 0.3}},
            scale=SCALE,
            minimum_confidence=0.5,
        )[0]
        self.assertEqual(row["status"], "insufficient_evidence")
        self.assertIsNone(row["priority"])
        self.assertIn("low_confidence_evidence", row["review_flags"])

    def test_stale_evidence_blocks_ranking(self):
        row = core.competency_gaps(
            {"a": 4},
            {
                "a": {
                    "level": 2,
                    "mean_confidence": 0.9,
                    "stale": True,
                }
            },
            scale=SCALE,
        )[0]
        self.assertEqual(row["status"], "insufficient_evidence")
        self.assertIn("stale_evidence", row["review_flags"])

    def test_evidence_aggregation_is_confidence_weighted(self):
        result = core.aggregate_evidence(
            [
                {
                    "skill": "analytics",
                    "level": 2,
                    "source": "assessment",
                    "confidence": 1.0,
                    "observed_on": "2026-09-01",
                },
                {
                    "skill": "analytics",
                    "level": 4,
                    "source": "self-rating",
                    "confidence": 0.5,
                    "observed_on": "2026-09-15",
                },
            ],
            scale=SCALE,
            as_of="2026-09-24",
        )
        self.assertAlmostEqual(
            result["analytics"]["level"],
            (2 * 1.0 + 4 * 0.5) / 1.5,
        )

    def test_evidence_aggregation_reports_sources(self):
        result = core.aggregate_evidence(
            [
                {
                    "skill": "analytics",
                    "level": 3,
                    "source": "work sample",
                    "confidence": 0.8,
                    "observed_on": "2026-09-01",
                    "evidence_type": "work_sample",
                }
            ],
            scale=SCALE,
            as_of="2026-09-24",
        )
        self.assertEqual(result["analytics"]["sources"], ["work sample"])
        self.assertEqual(
            result["analytics"]["evidence_types"],
            ["work_sample"],
        )

    def test_future_evidence_date_is_rejected(self):
        with self.assertRaises(ValueError):
            core.aggregate_evidence(
                [
                    {
                        "skill": "analytics",
                        "level": 3,
                        "source": "assessment",
                        "confidence": 0.8,
                        "observed_on": "2027-01-01",
                    }
                ],
                scale=SCALE,
                as_of="2026-09-24",
            )

    def test_stale_evidence_is_detected(self):
        result = core.aggregate_evidence(
            [
                {
                    "skill": "analytics",
                    "level": 3,
                    "source": "assessment",
                    "confidence": 0.8,
                    "observed_on": "2024-01-01",
                }
            ],
            scale=SCALE,
            as_of="2026-09-24",
            stale_after_days=365,
        )
        self.assertTrue(result["analytics"]["stale"])

    def test_prerequisite_graph_rejects_unknown_skill(self):
        with self.assertRaises(ValueError):
            core.validate_prerequisites(
                {"learning_analytics": ["statistics"]},
                {"learning_analytics"},
            )

    def test_prerequisite_graph_rejects_cycle(self):
        with self.assertRaises(ValueError):
            core.validate_prerequisites(
                {"a": ["b"], "b": ["a"]},
                {"a", "b"},
            )

    def test_prerequisite_blocker_is_reported(self):
        analysis = core.competency_gaps(
            REQUIRED,
            OBSERVED,
            scale=SCALE,
        )
        blockers = core.prerequisite_blockers(
            analysis,
            PREREQUISITES,
        )
        self.assertEqual(
            blockers["learning_analytics"][0]["skill"],
            "statistics",
        )

    def test_development_sequence_places_prerequisite_first(self):
        analysis = core.competency_gaps(
            REQUIRED,
            OBSERVED,
            scale=SCALE,
        )
        sequence = core.development_sequence(
            analysis,
            PREREQUISITES,
        )
        self.assertLess(
            sequence.index("statistics"),
            sequence.index("learning_analytics"),
        )

    def test_resource_validation_rejects_bad_levels(self):
        bad = [
            {
                "id": "bad",
                "title": "Bad",
                "competency": "statistics",
                "entry_level": 3,
                "target_level": 2,
                "effort_hours": 1,
                "modality": "course",
            }
        ]
        with self.assertRaises(ValueError):
            core.validate_resources(
                bad,
                scale=SCALE,
                competencies={"statistics"},
            )

    def test_resource_matching_requires_confirmed_gap(self):
        analysis = core.competency_gaps(
            REQUIRED,
            OBSERVED,
            scale=SCALE,
        )
        matches = core.match_resources(
            analysis,
            RESOURCES,
            scale=SCALE,
        )
        self.assertEqual(matches["facilitation"], [])
        self.assertTrue(matches["statistics"])

    def test_resource_matching_respects_entry_level(self):
        analysis = core.competency_gaps(
            {"statistics": 4},
            {"statistics": 1},
            scale=SCALE,
        )
        resources = [
            {
                "id": "advanced",
                "title": "Advanced Statistics",
                "competency": "statistics",
                "entry_level": 3,
                "target_level": 5,
                "effort_hours": 10,
                "modality": "course",
            }
        ]
        matches = core.match_resources(
            analysis,
            resources,
            scale=SCALE,
        )
        self.assertEqual(matches["statistics"], [])

    def test_resource_matching_prefers_target_reaching_resource(self):
        analysis = core.competency_gaps(
            {"statistics": 4},
            {"statistics": 2},
            scale=SCALE,
        )
        resources = [
            {
                "id": "partial",
                "title": "Partial",
                "competency": "statistics",
                "entry_level": 1,
                "target_level": 3,
                "effort_hours": 2,
                "modality": "course",
            },
            {
                "id": "full",
                "title": "Full",
                "competency": "statistics",
                "entry_level": 1,
                "target_level": 4,
                "effort_hours": 8,
                "modality": "course",
            },
        ]
        matches = core.match_resources(
            analysis,
            resources,
            scale=SCALE,
        )
        self.assertEqual(matches["statistics"][0]["id"], "full")

    def test_resource_prerequisite_blocks_match(self):
        analysis = core.competency_gaps(
            REQUIRED,
            OBSERVED,
            scale=SCALE,
        )
        matches = core.match_resources(
            analysis,
            RESOURCES,
            scale=SCALE,
        )
        self.assertEqual(matches["learning_analytics"], [])

    def test_plan_collects_evidence_before_training_unknown_skill(self):
        plan = core.build_development_plan(
            REQUIRED,
            OBSERVED,
            RESOURCES,
            prerequisites=PREREQUISITES,
            scale=SCALE,
        )
        facilitation = next(
            item for item in plan["items"]
            if item["skill"] == "facilitation"
        )
        self.assertEqual(facilitation["action"], "collect_evidence")

    def test_plan_sequences_statistics_before_learning_analytics(self):
        plan = core.build_development_plan(
            REQUIRED,
            OBSERVED,
            RESOURCES,
            prerequisites=PREREQUISITES,
            scale=SCALE,
        )
        self.assertLess(
            plan["sequence"].index("statistics"),
            plan["sequence"].index("learning_analytics"),
        )

    def test_plan_does_not_prescribe_training_for_exceeded_target(self):
        plan = core.build_development_plan(
            REQUIRED,
            OBSERVED,
            RESOURCES,
            prerequisites=PREREQUISITES,
            scale=SCALE,
        )
        skill = next(
            item for item in plan["items"]
            if item["skill"] == "instructional_design"
        )
        self.assertEqual(
            skill["action"],
            "no_development_required",
        )

    def test_legacy_resource_mapping_is_supported(self):
        plan = core.development_plan(
            {"a": 4},
            {"a": 2},
            {"a": ["Resource 1", "Resource 2"]},
            scale=SCALE,
        )
        item = next(
            item for item in plan["items"]
            if item["skill"] == "a"
        )
        self.assertEqual(len(item["resources"]), 2)

    def test_ranking_sensitivity_returns_scenarios(self):
        result = core.ranking_sensitivity(
            {"a": 4, "b": 4},
            {"a": 2, "b": 3},
            {
                "balanced": {"a": 1, "b": 1},
                "business_critical": {"a": 0.5, "b": 3},
            },
            scale=SCALE,
        )
        self.assertEqual(
            set(result["rankings"]),
            {"balanced", "business_critical"},
        )

    def test_ranking_sensitivity_detects_rank_change(self):
        result = core.ranking_sensitivity(
            {"a": 4, "b": 4},
            {"a": 2, "b": 3},
            {
                "gap_size": {"a": 1, "b": 1},
                "importance_shift": {"a": 0.1, "b": 4},
            },
            scale=SCALE,
        )
        self.assertFalse(result["rank_ranges"]["a"]["stable_rank"])

    def test_importance_unknown_skill_is_rejected(self):
        with self.assertRaises(ValueError):
            core.competency_gaps(
                {"a": 4},
                {"a": 2},
                {"b": 2},
                scale=SCALE,
            )

    def test_zero_confidence_evidence_is_unknown_for_level(self):
        summaries = core.aggregate_evidence(
            [
                {
                    "skill": "a",
                    "level": 3,
                    "source": "unverified",
                    "confidence": 0.0,
                    "observed_on": "2026-09-01",
                }
            ],
            scale=SCALE,
            as_of="2026-09-24",
        )
        rows = core.competency_gaps(
            {"a": 4},
            summaries,
            scale=SCALE,
        )
        self.assertEqual(rows[0]["status"], "unknown_evidence")


if __name__ == "__main__":
    unittest.main()
