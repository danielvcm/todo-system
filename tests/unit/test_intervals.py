import os
import sqlite3
import tempfile
import unittest
from ha.pyscripts.todo_db import run_migrations
from ha.pyscripts.todo_services import create_task, list_due


class TestIntervals(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_interval_inclusion_and_exclusion(self):
        task = {
            "title": "Interval Task",
            "start_due_date": "2026-06-10",
            "end_due_date": "2026-06-12",
        }
        res = create_task(task, db_path=self.db_path)
        tid = res["created_id"]

        # dates inside range
        r1 = list_due("2026-06-10", db_path=self.db_path)
        r2 = list_due("2026-06-11", db_path=self.db_path)
        r3 = list_due("2026-06-12", db_path=self.db_path)
        self.assertTrue(any(o["task_id"] == tid for o in r1["occurrences"]))
        self.assertTrue(any(o["task_id"] == tid for o in r2["occurrences"]))
        self.assertTrue(any(o["task_id"] == tid for o in r3["occurrences"]))

        # date outside range
        r4 = list_due("2026-06-13", db_path=self.db_path)
        self.assertFalse(any(o["task_id"] == tid for o in r4["occurrences"]))

    def test_invalid_interval_rejected(self):
        task = {
            "title": "Bad Interval",
            "start_due_date": "2026-06-20",
            "end_due_date": "2026-06-10",
        }
        with self.assertRaises(ValueError):
            create_task(task, db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
