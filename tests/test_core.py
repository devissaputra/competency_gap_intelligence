import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from competency_gap_intelligence import core


class CoreTests(unittest.TestCase):
    def test_gap_priority_and_resource_plan(self):
        gaps = core.competency_gaps({"a": 4, "b": 3}, {"a": 2, "b": 2}, {"a": 2, "b": 1})
        self.assertEqual(gaps[0]["skill"], "a")
        self.assertEqual(gaps[0]["gap"], 2)
        plan = core.development_plan({"a": 4}, {"a": 2}, {"a": ["r1", "r2"]})
        self.assertEqual(plan[0]["resources"], ["r1", "r2"])

    def test_negative_levels_are_rejected(self):
        with self.assertRaises(ValueError):
            core.competency_gaps({"a": 4}, {"a": -1})


if __name__ == "__main__":
    unittest.main()
