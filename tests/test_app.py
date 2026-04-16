import importlib
import os
import tempfile
import unittest


class TaskManagerApiTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["DATABASE_PATH"] = os.path.join(self.temp_dir.name, "test.db")
        os.environ["SECRET_KEY"] = "test-secret-key"

        import app as app_module

        self.app_module = importlib.reload(app_module)
        self.client = self.app_module.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registration_login_and_task_lifecycle(self):
        response = self.client.post(
            "/api/register",
            json={"username": "alice", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            "/api/login",
            json={"username": "alice", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/tasks",
            json={"title": "Write tests", "description": "Cover auth and task flow"},
        )
        self.assertEqual(response.status_code, 201)
        task_id = response.get_json()["task"]["id"]

        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["tasks"]), 1)

        response = self.client.post(f"/api/tasks/{task_id}/toggle")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["task"]["done"])

        response = self.client.delete(f"/api/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["tasks"], [])


if __name__ == "__main__":
    unittest.main()