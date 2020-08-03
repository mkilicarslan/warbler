"""Message model tests."""
# run these tests like:
#
# python -m unittest test_message_model.py

import os
from unittest import TestCase
from datetime import datetime

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        user_id = u.id

        # New message
        m = Message(
            text='Message text',
            timestamp=datetime.now(),
            user_id=user_id
        )
        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(u.messages), 1)

        # __repr__ method
        self.assertEqual(str(m), f"<Message #{m.id}: {m.user_id}, {m.timestamp}>")

        # message without timesamp should set timestamp as now
        m2 = Message(text='Msg text', user_id=user_id)
        db.session.add(m2)
        db.session.commit()
        self.assertIsNotNone(m2.timestamp)

        # message without text should raise IntegrityError
        m3 = Message(user_id=user_id)
        db.session.add(m3)
        self.assertIsNotNone(IntegrityError, db.session.commit)
