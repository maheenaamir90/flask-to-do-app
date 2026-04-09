import unittest
import warnings

from app import create_app, db
from app.models import Task, User

# Keep test output clean for demo/report capture.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        # Use in-memory DB for isolated, clean test runs.
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        # Disable CSRF in tests so form posts can be exercised directly.
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.app.config["TESTING"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()

        # Reset DB state for each test run.
        db.drop_all()
        db.create_all()

        self.client = self.app.test_client()

        self.u1 = User(username="alice")
        self.u1.set_password("pass123")
        self.u2 = User(username="bob")
        self.u2.set_password("pass123")
        db.session.add_all([self.u1, self.u2])
        db.session.commit()

        t1 = Task(title="Alice Task", owner=self.u1)
        t2 = Task(title="Bob Task", owner=self.u2)
        db.session.add_all([t1, t2])
        db.session.commit()
        self.bob_task_id = t2.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def login(self, username, password):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )

    def test_unauthenticated_redirect_from_index(self):
        resp = self.client.get("/", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers.get("Location", ""))

    def test_authenticated_user_sees_only_own_tasks(self):
        self.login("alice", "pass123")
        resp = self.client.get("/", follow_redirects=True)
        body = resp.get_data(as_text=True)
        self.assertIn("Alice Task", body)
        self.assertNotIn("Bob Task", body)

    def test_idor_block_foreign_task_edit(self):
        self.login("alice", "pass123")
        resp = self.client.get(f"/tasks/{self.bob_task_id}/edit", follow_redirects=False)
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()


class CsrfEnforcementTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        # Use in-memory DB for isolated, clean test runs.
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["TESTING"] = True
        # Keep CSRF enabled for this test case on purpose.
        self.app.config["WTF_CSRF_ENABLED"] = True

        self.ctx = self.app.app_context()
        self.ctx.push()

        db.drop_all()
        db.create_all()

        self.client = self.app.test_client()
        user = User(username="csrf_user")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def test_create_task_without_csrf_token_is_rejected(self):
        # Simulate logged-in session and then submit POST without csrf_token.
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.user_id)
            session["_fresh"] = True

        resp = self.client.post("/tasks/create", data={"title": "No CSRF token"})
        self.assertEqual(resp.status_code, 400)

    def test_logout_without_csrf_token_is_rejected(self):
        # Logout is POST-only and CSRF-protected; missing token must be rejected.
        with self.client.session_transaction() as session:
            session["_user_id"] = str(self.user_id)
            session["_fresh"] = True

        resp = self.client.post("/logout")
        self.assertEqual(resp.status_code, 400)
