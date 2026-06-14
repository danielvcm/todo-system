import os
import sqlite3
import tempfile
import unittest
from ha.pyscripts.todo_db import run_migrations
from ha.pyscripts.todo_services import list_due


class TestListDue(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_due_date_and_persisted_occurrence(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # create a task with explicit due_date
        cur.execute(
            "INSERT INTO tasks(title, description, due_date) VALUES(?,?,?)",
            ("Buy milk", "Buy milk description", "2026-06-14"),
        )
        task_id = cur.lastrowid
        # create a persisted occurrence for another task
        cur.execute(
            "INSERT INTO tasks(title) VALUES(?)", ("Persisted task",)
        )
        t2 = cur.lastrowid
        cur.execute(
            "INSERT INTO occurrences(task_id, due_date) VALUES(?,?)", (t2, "2026-06-14")
        )
        conn.commit()
        conn.close()

        res = list_due("2026-06-14", db_path=self.db_path)
        occs = res.get("occurrences", [])
        # Expect two occurrences: the explicit due_date task and the persisted occurrence
        self.assertEqual(len(occs), 2)
        ids = sorted([o["task_id"] for o in occs])
        self.assertEqual(ids, [task_id, t2])

    def test_recurrence_interval(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # create recurring task starting 2026-06-12 every 2 days
        rule = '{"interval_days": 2}'
        cur.execute(
            "INSERT INTO tasks(title, start_due_date, recurrence_rule) VALUES(?,?,?)",
            ("Water plants", "2026-06-12", rule),
        )
        task_id = cur.lastrowid
        conn.commit()
        conn.close()

        # 2026-06-14 is 2 days after 2026-06-12 -> should be included
        res = list_due("2026-06-14", db_path=self.db_path)
        occs = res.get("occurrences", [])
        self.assertEqual(len(occs), 1)
        self.assertEqual(occs[0]["task_id"], task_id)


if __name__ == "__main__":
    unittest.main()
