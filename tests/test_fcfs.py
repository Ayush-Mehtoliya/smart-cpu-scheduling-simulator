
import unittest

from scheduler.fcfs import fcfs


class TestFCFS(unittest.TestCase):
    def test_basic_scheduling(self):
        processes = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 5},
            {"pid": "P2", "arrival_time": 1, "burst_time": 3},
            {"pid": "P3", "arrival_time": 2, "burst_time": 1},
        ]

        result = fcfs(processes)
        rows = {p["pid"]: p for p in result["processes"]}

        self.assertEqual(rows["P1"]["completion_time"], 5)
        self.assertEqual(rows["P2"]["completion_time"], 8)
        self.assertEqual(rows["P3"]["completion_time"], 9)

        self.assertEqual(rows["P1"]["waiting_time"], 0)
        self.assertEqual(rows["P2"]["waiting_time"], 4)
        self.assertEqual(rows["P3"]["waiting_time"], 6)

        self.assertEqual(rows["P2"]["response_time"], 4)
        self.assertAlmostEqual(result["averages"]["waiting_time"], 10 / 3)

    def test_idle_cpu(self):
        processes = [
            {"pid": "P1", "arrival_time": 3, "burst_time": 2},
        ]

        result = fcfs(processes)

        self.assertEqual(result["gantt"], [
            {"pid": "IDLE", "start": 0, "end": 3},
            {"pid": "P1", "start": 3, "end": 5},
        ])

        self.assertEqual(result["processes"][0]["waiting_time"], 0)

    def test_invalid_burst_time(self):
        with self.assertRaises(ValueError):
            fcfs([
                {"pid": "P1", "arrival_time": 0, "burst_time": 0},
            ])


if __name__ == "__main__":
    unittest.main()
