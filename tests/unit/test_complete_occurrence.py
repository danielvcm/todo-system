import os
import sqlite3
import tempfile
import unittest
from ha.pyscripts.todo_db import run_migrations
from ha.pyscripts.todo_services import create_task, complete_occurrence, get_task_history


class TestCompleteOccurrence(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_complete_new_occurrence(self):
        """Complete an occurrence that doesn't exist yet (creates it)."""
        task = {"title": "Test Task"}
        res = create_task(task, db_path=self.db_path)
        task_id = res["created_id"]

        # Complete an occurrence that doesn't exist yet
        res = complete_occurrence(task_id, "2026-06-15", db_path=self.db_path)
        self.assertIn("completed", res)
        comp = res["completed"]
        self.assertEqual(comp["task_id"], task_id)
        self.assertEqual(comp["due_date"], "2026-06-15")
        self.assertIsNotNone(comp["completed_at"])

    def test_complete_existing_occurrence(self):
        """Complete an occurrence that already exists (updates it)."""
        task = {"title": "Test Task"}
        res = create_task(task, db_path=self.db_path)
        task_id = res["created_id"]

        # Insert persisted occurrence without completion
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO occurrences(task_id, due_date) VALUES(?,?)",
            (task_id, "2026-06-15"),
        )
        occ_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Now complete it
        res = complete_occurrence(task_id, "2026-06-15", db_path=self.db_path)
        comp = res["completed"]
        self.assertEqual(comp["occurrence_id"], occ_id)
        self.assertIsNotNone(comp["completed_at"])

    def test_task_history_empty(self):
        """Get history for a task with no completed occurrences."""
        task = {"title": "Test Task"}
        res = create_task(task, db_path=self.db_path)
        task_id = res["created_id"]

        hist = get_task_history(task_id, db_path=self.db_path)
        self.assertEqual(hist["task_id"], task_id)
        self.assertEqual(hist["total"], 0)
        self.assertEqual(len(hist["occurrences"]), 0)

    def test_task_history_pagination(self):
        """Test pagination of task history."""
        task = {"title": "Test Task"}
        res = create_task(task, db_path=self.db_path)
        task_id = res["created_id"]

        # Complete multiple occurrences
        for i in range(5):
            complete_occurrence(task_id, f"2026-06-{10+i:02d}", db_path=self.db_path)

        # Get first page (limit=2)
        hist1 = get_task_history(task_id, limit=2, offset=0, db_path=self.db_path)
        self.assertEqual(hist1["total"], 5)
        self.assertEqual(len(hist1["occurrences"]), 2)

        # Get second page (limit=2, offset=2)
        hist2 = get_task_history(task_id, limit=2, offset=2, db_path=self.db_path)
        self.assertEqual(len(hist2["occurrences"]), 2)

        # Get remaining (limit=2, offset=4)
        hist3 = get_task_history(task_id, limit=2, offset=4, db_path=self.db_path)
        self.assertEqual(len(hist3["occurrences"]), 1)


if __name__ == "__main__":
    unittest.main()
