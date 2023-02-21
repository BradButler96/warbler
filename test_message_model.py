#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()


    def test_message_info(self):

        user = User(username="testuser", email="test@test.com", password="testuser", image_url=None)
        db.session.add(user)
        db.session.commit()

        msg = Message(text='This is a valid msg', user_id=user.id)
        db.session.add(msg)
        timestamp = datetime.utcnow().replace(microsecond=0)
        db.session.commit()

        self.assertEqual(msg.text, 'This is a valid msg')
        self.assertEqual(msg.timestamp.replace(microsecond=0), timestamp)
        self.assertEqual(msg.user_id, user.id)
        self.assertIn(': testuser, test@test.com>', str(msg.user))

    def test_message_text_limit(self):
        """msg length > 140 characters"""

        user = User(username="testuser", email="test@test.com", password="testuser", image_url=None)
        db.session.add(user)
        db.session.commit()

        msg = Message(text='ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-ABABABABA-1', 
                      user_id=user.id)

        db.session.add(msg)

        with self.assertRaises(DataError):
            db.session.commit()


