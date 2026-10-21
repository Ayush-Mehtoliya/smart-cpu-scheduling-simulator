
import unittest

from scheduler.srtf import srtf


class TestSRTF(unittest.TestCase):
    def test_preemption(self):
        processes = [
            {"pid": "P1", "arrival_time": 0, "burst_time": 7},
            {"pid": "P2", "arrival_time": 2, "burst_time": 4},
            {"pid": "P3", "arrival_time": 4, "burst_time": 1},
        ]

        result = srtf(processes)
        rows = {p["pid"]: p for p in result["processes"]}

        self.assertEqual(rows["P1"]["completion_time"], 12)
        self.assertEqual(rows["P2"]["completion_time"], 7)
        self.assertEqual(rows["P3"]["completion_time"], 5)

        self.assertEqual(rows["P1"]["waiting_time"], 5)
        self.assertEqual(rows["P2"]["waiting_time"], 1)
        self.assertEqual(rows["P3"]["waiting_time"], 0)

        self.assertEqual(
            [(g["pid"], g["start"], g["end"]) for g in result["gantt"]],
            [
                ("P1", 0, 2),
                ("P2", 2, 4),
                ("P3", 4, 5),
                ("P2", 5, 7),
                ("P1", 7, 12),
            ],
        )

    def test_idle_cpu(self):
        result = srtf([
            {"pid": "P1", "arrival_time": 3, "burst_time": 2},
        ])

        self.assertEqual(result["gantt"], [
            {"pid": "IDLE", "start": 0, "end": 3},
            {"pid": "P1", "start": 3, "end": 5},
        ])

    def test_invalid_burst_rejected(self):
        with self.assertRaises(ValueError):
            srtf([
                {"pid": "P1", "arrival_time": 0, "burst_time": 0},
            ])


if __name__ == "__main__":
    unittest.main()
