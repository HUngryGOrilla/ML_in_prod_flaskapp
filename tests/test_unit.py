import os
import unittest
from datetime import date, timedelta
from unittest import mock

from models import User, Task
from app import _build_postgres_uri

class TestUnitCases(unittest.TestCase):
    
    # Test Task.is_overdue()
    def test_task_is_overdue(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        t1 = Task(title="Late", due_date=yesterday, is_completed=False)
        self.assertTrue(t1.is_overdue(), "Task due yesterday should be overdue")
        t2 = Task(title="Future", due_date=tomorrow, is_completed=False)
        self.assertFalse(t2.is_overdue(), "Task due tomorrow should NOT be overdue")
        t3 = Task(title="Done Late", due_date=yesterday, is_completed=True)
        self.assertFalse(t3.is_overdue(), "Completed task should NOT be overdue, even if late")
        t4 = Task(title="No Date", due_date=None, is_completed=False)
        self.assertFalse(t4.is_overdue(), "Task with no due date cannot be overdue")


    # Test User Password Logic
    def test_user_password_logic(self):

        u = User(username="test_user")
        u.set_password("flask_rules")
        self.assertNotEqual(u.password_hash, "flask_rules", "Password should be hashed, not plain text")
        self.assertTrue(u.check_password("flask_rules"), "Correct password should return True")
        self.assertFalse(u.check_password("wrong_password"), "Wrong password should return False")


    # Test Environment Variable Parsing
    @mock.patch.dict(os.environ, {
        "DATABASE_URL": "",  
        "POSTGRES_USER": "unit_user",
        "POSTGRES_PASSWORD": "unit_pass",
        "POSTGRES_HOST": "unit_host",
        "POSTGRES_PORT": "9999",
        "POSTGRES_DB": "unit_db"
    })
    def test_build_postgres_uri(self):
        expected_uri = "postgresql+psycopg2://unit_user:unit_pass@unit_host:9999/unit_db"
        actual_uri = _build_postgres_uri()
        
        self.assertEqual(actual_uri, expected_uri, "URI was not built correctly from env vars")

if __name__ == "__main__":
    unittest.main()