
import unittest

from scheduler.sjf import sjf


class TestSJF(unittest.TestCase):
    def test_shortest_available_job_runs_first(self):
        processes = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 7},
            {"pid": "P2", "arrival_time": 2, "burst_time": 4},
            {"pid": "P3", "arrival_time": 4, "burst_time": 1},
        ]

        result = sjf(processes)

        self.assertEqual(
            [(g["pid"], g["start"], g["end"]) for g in result["gantt"]],
            [("P1", 0, 7), ("P3", 7, 8), ("P2", 8, 12)],
        )

        rows = {p["pid"]: p for p in result["processes"]}
        self.assertEqual(rows["P2"]["waiting_time"], 6)
        self.assertEqual(rows["P3"]["waiting_time"], 3)
        self.assertEqual(rows["P3"]["response_time"], 3)

    def test_idle_cpu(self):
        result = sjf([
            {"pid": "P1", "arrival_time": 5, "burst_time": 2},
        ])

        self.assertEqual(result["gantt"], [
            {"pid": "IDLE", "start": 0, "end": 5},
            {"pid": "P1", "start": 5, "end": 7},
        ])

    def test_duplicate_pid_rejected(self):
        with self.assertRaises(ValueError):
            sjf([
                {"pid": "P1", "arrival_time": 0, "burst_time": 2},
                {"pid": "P1", "arrival_time": 1, "burst_time": 3},
            ])


if __name__ == "__main__":
    unittest.main()
