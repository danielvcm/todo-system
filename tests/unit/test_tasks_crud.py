import os
import sqlite3
import tempfile
import unittest
from ha.pyscripts.todo_db import run_migrations
from ha.pyscripts.todo_services import create_task, update_task, delete_task


class TestTasksCRUD(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_create_task_valid(self):
        task = {"title": "Test Create", "due_date": "2026-06-15"}
        res = create_task(task, db_path=self.db_path)
        self.assertIn("created_id", res)
        tid = res["created_id"]
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT title, due_date FROM tasks WHERE id = ?", (tid,))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Test Create")
        self.assertEqual(row[1], "2026-06-15")
        conn.close()

    def test_update_and_delete_task(self):
        # create
        task = {"title": "To Update"}
        res = create_task(task, db_path=self.db_path)
        tid = res["created_id"]
        # update
        upd = update_task(tid, {"title": "Updated Title"}, db_path=self.db_path)
        self.assertEqual(upd["updated_id"], tid)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT title FROM tasks WHERE id = ?", (tid,))
        row = cur.fetchone()
        self.assertEqual(row[0], "Updated Title")
        # delete
        d = delete_task(tid, db_path=self.db_path)
        self.assertEqual(d["deleted_id"], tid)
        cur.execute("SELECT id FROM tasks WHERE id = ?", (tid,))
        self.assertIsNone(cur.fetchone())
        conn.close()


if __name__ == "__main__":
    unittest.main()
