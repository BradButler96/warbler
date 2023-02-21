"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
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


    def test_repr(self):
        """Does __repr__ return the proper notation"""

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(user)
        db.session.commit()

        self.assertIn(': testuser, test@test.com>', repr(user))


    def test_user_follows(self):

        user1 = User.signup('test_user_1', 'test@test.com', 'TestPassword', None)
        user2 = User.signup('test_user_2', 'test2@test2.com', 'TestPassword2', None)
        db.session.commit()

        self.assertEqual(len(user1.followers), 0)
        self.assertEqual(len(user2.following), 0)
        self.assertEqual(len(user2.followers), 0)
        self.assertEqual(len(user1.following), 0)

        user2.following.append(user1)
        db.session.commit()

        self.assertEqual(len(user1.followers), 1)
        self.assertEqual(len(user2.following), 1)
        self.assertEqual(len(user2.followers), 0)
        self.assertEqual(len(user1.following), 0)


    def test_is_following(self):

        user1 = User.signup('test_user_1', 'test@test.com', 'TestPassword', None)
        user2 = User.signup('test_user_2', 'test2@test2.com', 'TestPassword2', None)
        db.session.commit()

        self.assertFalse(user2.is_following(user1))

        user2.following.append(user1)
        db.session.commit()

        self.assertTrue(user2.is_following(user1))


    def test_is_followed_by(self):

        user1 = User.signup('test_user_1', 'test@test.com', 'TestPassword', None)
        user2 = User.signup('test_user_2', 'test2@test2.com', 'TestPassword2', None)
        db.session.commit()

        self.assertFalse(user1.is_followed_by(user2))

        user2.following.append(user1)
        db.session.commit()

        self.assertTrue(user1.is_followed_by(user2))


    def test_signup_valid(self):

        user = User.signup('valid_test_user', 'test@test.com', 'TestPassword', None)
        db.session.commit()
        
        user_test = User.query.filter(User.username == 'valid_test_user').first()

        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "valid_test_user")
        self.assertNotEqual(user_test.password, "TestPassword")
        self.assertTrue(user_test.password.startswith("$2b$"))

    
    def test_signup_invalid_username(self):

        user = User.signup(None, "test2@test.com", "TestPassword", None)

        with self.assertRaises(IntegrityError):
            db.session.commit()

    
    def test_signup_invalid_email(self):

        user = User.signup("valid_test_user", None, "TestPassword", None)

        with self.assertRaises(IntegrityError):
            db.session.commit()
            
    
    def test_signup_invalid_password(self):
        
        with self.assertRaises(ValueError):
            User.signup("valid_test_user", "test2@test.com", None, None)


    def test_authenticate_valid(self):

        user = User.signup('valid_test_user', 'test@test.com', 'TestPassword', None)
        db.session.commit()

        self.assertEqual(User.authenticate('valid_test_user', 'TestPassword'), user)
        self.assertNotEqual(User.authenticate('valid_test_user', 'TestPassword'), False)


    def test_authenticate_invalid_username(self):

        user = User.signup('valid_test_user', 'test@test.com', 'TestPassword', None)
        db.session.commit()

        self.assertEqual(User.authenticate('invalid_test_user', 'TestPassword'), False)
        self.assertNotEqual(User.authenticate('invalid_test_user', 'TestPassword'), user)


    def test_authenticate_invalid_password(self):

        user = User.signup('valid_test_user', 'test@test.com', 'TestPassword', None)
        db.session.commit()

        self.assertEqual(User.authenticate('valid_test_user', 'NotTestPassword'), False)
        self.assertNotEqual(User.authenticate('invalid_test_user', 'NotTestPassword'), user)