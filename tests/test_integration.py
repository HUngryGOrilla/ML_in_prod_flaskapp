import unittest
import os
from unittest import mock
from app import create_app
from extensions import db
from models import User, Task

class TestIntegrationCases(unittest.TestCase):
    
    def setUp(self):
        self.env_patcher = mock.patch.dict(os.environ, {
            "DATABASE_URL": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret"
        })
        self.env_patcher.start()
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.env_patcher.stop()

    #  Test Register + Login Flow 
    def test_auth_flow(self):
        response = self.client.post('/register', data={
            'username': 'integration_user',
            'password': 'password123',
            'confirm': 'password123'
        }, follow_redirects=True)
        self.assertIn(b"Registration successful", response.data)

        response = self.client.post('/login', data={
            'username': 'integration_user',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b"Logged in successfully", response.data)
        self.assertIn(b"integration_user", response.data)

        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b"You have been logged out", response.data)

    #  Test 2: Creating a Task via POST 
    def test_create_task(self):
        self._login_user()

        response = self.client.post('/tasks/new', data={
            'title': 'Integration Task',
            'description': 'Testing creation',
            'due_date': '2025-12-31'
        }, follow_redirects=True)
        
        self.assertIn(b"Task created", response.data)
        self.assertIn(b"Integration Task", response.data)

        with self.app.app_context():
            task = Task.query.filter_by(title='Integration Task').first()
            self.assertIsNotNone(task)
            self.assertEqual(task.description, 'Testing creation')

    #  Test 3: Editing and Toggling a Task 
    def test_edit_and_toggle_task(self):
        self._login_user()
        
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            task = Task(title="Original Title", user_id=user.id)
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = self.client.post(f'/tasks/{task_id}/edit', data={
            'title': 'Updated Title',
            'description': 'Updated Desc',
            'due_date': '',
            'is_completed': '' 
        }, follow_redirects=True)
        self.assertIn(b"Task updated", response.data)
        self.assertIn(b"Updated Title", response.data)

        response = self.client.post(f'/tasks/{task_id}/toggle', follow_redirects=True)
        self.assertIn(b"Task status updated", response.data)
        
        with self.app.app_context():
            task = Task.query.get(task_id)
            self.assertTrue(task.is_completed)

    def _login_user(self):
        with self.app.app_context():
            u = User(username='testuser')
            u.set_password('pass')
            db.session.add(u)
            db.session.commit()
        
        self.client.post('/login', data={'username': 'testuser', 'password': 'pass'})

if __name__ == "__main__":
    unittest.main()