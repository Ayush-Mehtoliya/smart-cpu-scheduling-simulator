
import unittest

from scheduler.round_robin import round_robin


class TestRoundRobin(unittest.TestCase):

    def test_basic_scheduling(self):
        result = round_robin([
            {"pid": "P1", "arrival_time": 0, "burst_time": 5},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3},
        ], quantum=2)

        self.assertEqual(
            [(g["pid"], g["start"], g["end"])
             for g in result["gantt"]],
            [
                ("P1", 0, 2),
                ("P2", 2, 4),
                ("P1", 4, 6),
                ("P2", 6, 7),
                ("P1", 7, 8),
            ],
        )

        rows = {p["pid"]: p for p in result["processes"]}
        self.assertEqual(rows["P1"]["completion_time"], 8)
        self.assertEqual(rows["P1"]["waiting_time"], 3)
        self.assertEqual(rows["P2"]["completion_time"], 7)
        self.assertEqual(rows["P2"]["waiting_time"], 3)

    def test_idle_cpu(self):
        result = round_robin([
            {"pid": "P1", "arrival_time": 4, "burst_time": 3},
        ], quantum=2)

        self.assertEqual(result["gantt"], [
            {"pid": "IDLE", "start": 0, "end": 4},
            {"pid": "P1", "start": 4, "end": 6},
            {"pid": "P1", "start": 6, "end": 7},
        ])

    def test_invalid_quantum_rejected(self):
        with self.assertRaises(ValueError):
            round_robin([
                {"pid": "P1", "arrival_time": 0, "burst_time": 2},
            ], quantum=0)

    def test_duplicate_pid_rejected(self):
        with self.assertRaises(ValueError):
            round_robin([
                {"pid": "P1", "arrival_time": 0, "burst_time": 2},
                {"pid": "P1", "arrival_time": 1, "burst_time": 3},
            ], quantum=2)


if __name__ == "__main__":
    unittest.main()
