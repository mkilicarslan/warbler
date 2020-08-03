"""User model tests."""

# run these tests like:
# 
# python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # __repr__ method
        self.assertEqual(str(u), f"<User #{u.id}: {u.username}, {u.email}>")

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        db.session.add(u)
        db.session.commit()

        # is_following and is_followed_by methods
        self.assertEqual(u.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u), False)

        u.following.append(u2)
        db.session.commit()

        self.assertEqual(u.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u), True)

        # signup
        sign_up_username = 'user_name'
        sign_up_email = 'signup@email.com'
        sign_up_password = 'password'
        sign_up_image_url = 'image.url.com'

        signed_up_user = User.signup(sign_up_username, sign_up_email, sign_up_password, sign_up_image_url)
        db.session.commit()
        self.assertIsNotNone(signed_up_user)
        self.assertIsNotNone(signed_up_user.id)

        signed_up_user = User.signup(sign_up_username, sign_up_email, sign_up_password, sign_up_image_url)
        self.assertRaises(IntegrityError, db.session.commit)
        self.assertRaises(TypeError, User.signup, sign_up_username, sign_up_email)
        db.session.rollback()

        # authenticate
        auth_user = User.authenticate(sign_up_username, sign_up_password)
        self.assertIsInstance(auth_user, User)
        auth_user = User.authenticate(sign_up_username, '123')
        self.assertNotIsInstance(auth_user, User)
        auth_user = User.authenticate('ABC', sign_up_password)
        self.assertNotIsInstance(auth_user, User)
