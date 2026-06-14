import unittest
from ha.pyscripts.recurrence import parse_recurrence, expand


class TestRecurrence(unittest.TestCase):
    def test_parse_simple_json(self):
        r = parse_recurrence('{"interval_days": 3}')
        self.assertIsInstance(r, dict)
        self.assertEqual(r.get("interval_days"), 3)

    def test_expand_interval(self):
        task = {"id": 1, "start_due_date": "2026-06-10", "recurrence_rule": '{"interval_days": 2}'}
        # 2026-06-12 should be included (2 days after start)
        out = expand(task, "2026-06-12")
        self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
