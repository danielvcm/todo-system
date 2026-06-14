import os
import sqlite3
import tempfile
import unittest
from ha.pyscripts.todo_db import run_migrations
from ha.pyscripts.todo_services import (
    list_users,
    sync_users_from_ha,
    create_user,
    get_user_by_ha_id,
    create_task,
    handle_request,
)


class TestUserSync(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_list_users_empty(self):
        """List users when none exist."""
        res = list_users(db_path=self.db_path)
        self.assertEqual(res["users"], [])

    def test_sync_users_from_ha(self):
        """Sync HA users into users table."""
        ha_users = [
            {"user_id": "user_001", "username": "alice"},
            {"user_id": "user_002", "username": "bob"},
        ]
        res = sync_users_from_ha(ha_users, db_path=self.db_path)
        self.assertEqual(res["synced"], 2)

        # Verify they were inserted
        users_res = list_users(db_path=self.db_path)
        self.assertEqual(len(users_res["users"]), 2)
        usernames = [u["username"] for u in users_res["users"]]
        self.assertIn("alice", usernames)
        self.assertIn("bob", usernames)

    def test_sync_upsert_behavior(self):
        """Sync updates existing users instead of duplicating."""
        ha_users = [
            {"user_id": "user_001", "username": "alice_v1"},
        ]
        sync_users_from_ha(ha_users, db_path=self.db_path)

        # Sync same user_id with different username
        ha_users = [
            {"user_id": "user_001", "username": "alice_v2"},
        ]
        res = sync_users_from_ha(ha_users, db_path=self.db_path)
        self.assertEqual(res["synced"], 1)

        # Verify only one user exists and username was updated
        users_res = list_users(db_path=self.db_path)
        self.assertEqual(len(users_res["users"]), 1)
        self.assertEqual(users_res["users"][0]["username"], "alice_v2")

    def test_create_user_explicit(self):
        """Create user explicitly (admin convenience)."""
        res = create_user("user_admin", "admin", db_path=self.db_path)
        self.assertEqual(res["ha_user_id"], "user_admin")
        self.assertEqual(res["username"], "admin")
        self.assertIn("created_id", res)

        # Verify user exists
        user = get_user_by_ha_id("user_admin", db_path=self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "admin")

    def test_create_user_duplicate_error(self):
        """Creating duplicate user raises error."""
        create_user("user_001", "alice", db_path=self.db_path)
        with self.assertRaises(ValueError):
            create_user("user_001", "alice_duplicate", db_path=self.db_path)

    def test_get_user_by_ha_id_lookup(self):
        """Look up user by HA user_id."""
        create_user("user_lookup", "lookup_user", db_path=self.db_path)
        user = get_user_by_ha_id("user_lookup", db_path=self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "lookup_user")
        self.assertEqual(user["ha_user_id"], "user_lookup")

    def test_get_user_by_ha_id_not_found(self):
        """Looking up non-existent user returns None."""
        user = get_user_by_ha_id("nonexistent", db_path=self.db_path)
        self.assertIsNone(user)

    def test_handle_request_list_users(self):
        """Test handle_request for list_users action."""
        create_user("user_001", "alice", db_path=self.db_path)
        create_user("user_002", "bob", db_path=self.db_path)

        payload = handle_request(
            "list_users",
            {"db_path": self.db_path},
            calling_user_id="user_001",
        )
        self.assertEqual(len(payload["users"]), 2)

    def test_handle_request_sync_users(self):
        """Test handle_request for sync_users_from_ha action."""
        ha_users = [
            {"user_id": "ha_001", "username": "ha_alice"},
            {"user_id": "ha_002", "username": "ha_bob"},
        ]
        payload = handle_request(
            "sync_users_from_ha",
            {"ha_users": ha_users, "db_path": self.db_path},
            calling_user_id="admin",
        )
        self.assertEqual(payload["synced"], 2)

    def test_handle_request_create_user(self):
        """Test handle_request for create_user action."""
        payload = handle_request(
            "create_user",
            {
                "ha_user_id": "user_new",
                "username": "new_user",
                "db_path": self.db_path,
            },
            calling_user_id="admin",
        )
        self.assertIn("created_id", payload)
        self.assertEqual(payload["username"], "new_user")


class TestUserAssignment(unittest.TestCase):
    """Test task assignment to users and permission context."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        run_migrations(self.db_path)

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except Exception:
            pass

    def test_create_task_with_assignee(self):
        """Create task assigned to a user."""
        # Create user first
        create_user("user_alice", "alice", db_path=self.db_path)

        # Create task assigned to that user
        task = {
            "title": "Buy milk",
            "assignee_ha_user_id": "user_alice",
        }
        res = create_task(task, db_path=self.db_path)
        task_id = res["created_id"]

        # Verify task has assignee
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT assignee_ha_user_id FROM tasks WHERE id = ?", (task_id,)
        )
        row = cur.fetchone()
        self.assertEqual(row[0], "user_alice")
        conn.close()

    def test_permission_context_in_request(self):
        """Test that calling_user_id is passed through handle_request."""
        create_user("user_alice", "alice", db_path=self.db_path)

        # Create task with explicit calling_user_id context
        payload = handle_request(
            "create_task",
            {
                "task": {"title": "Assigned task", "assignee_ha_user_id": "user_alice"},
                "db_path": self.db_path,
            },
            calling_user_id="user_alice",
        )
        self.assertIn("created_id", payload)


if __name__ == "__main__":
    unittest.main()
