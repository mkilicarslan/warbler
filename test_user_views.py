"""User View tests."""
# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_views.py

from models import db, connect_db, Message, User
from unittest import TestCase
import os


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testuser2",
                                     image_url=None)

        db.session.commit()

    def test_signup(self):
        """Can user sign up?"""

        with self.client as c:
            resp = c.get("/signup")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('E-mail', html)

            resp = c.post("/signup", data={
                "username": "user_name",
                "password": "password",
                "email": "emali@email.com"
            })

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            user = User.query.filter_by(email="emali@email.com")
            self.assertIsNotNone(user)

    def test_login(self):
        """Can user log in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/login")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('Username', html)

            resp = c.post("/login", data={
                "username": "testuser",
                "password": "testuser",
            })

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

    def test_list_users(self):
        """Can anyone see user listing?"""

        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)

    def test_user_detail(self):
        """Can anyone see user detail page?"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)

    def test_follower_pages(self):
        """Can only logged in users see follower/following pages?"""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/following")
            # redirects to homepage
            self.assertEqual(resp.status_code, 302)
            resp = c.get(f"/users/{self.testuser.id}/followers")
            self.assertEqual(resp.status_code, 302)

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)
            self.assertIn(self.testuser.username, html)
