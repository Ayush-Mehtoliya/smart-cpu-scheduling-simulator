
import unittest

from scheduler.priority import priority_scheduling


class TestPriority(unittest.TestCase):
    def test_higher_priority_runs_first(self):
        result = priority_scheduling([
            {"pid": "P1", "arrival_time": 0, "burst_time": 4, "priority": 3},
            {"pid": "P2", "arrival_time": 0, "burst_time": 2, "priority": 1},
            {"pid": "P3", "arrival_time": 1, "burst_time": 1, "priority": 2},
        ])

        self.assertEqual(
            [(g["pid"], g["start"], g["end"]) for g in result["gantt"]],
            [("P2", 0, 2), ("P3", 2, 3), ("P1", 3, 7)],
        )

        rows = {p["pid"]: p for p in result["processes"]}
        self.assertEqual(rows["P1"]["waiting_time"], 3)
        self.assertEqual(rows["P3"]["waiting_time"], 1)
        self.assertEqual(rows["P2"]["waiting_time"], 0)

    def test_idle_cpu(self):
        result = priority_scheduling([
            {"pid": "P1", "arrival_time": 4, "burst_time": 2, "priority": 1},
        ])

        self.assertEqual(result["gantt"], [
            {"pid": "IDLE", "start": 0, "end": 4},
            {"pid": "P1", "start": 4, "end": 6},
        ])

    def test_missing_priority_rejected(self):
        with self.assertRaises(ValueError):
            priority_scheduling([
                {"pid": "P1", "arrival_time": 0, "burst_time": 2},
            ])


if __name__ == "__main__":
    unittest.main()
