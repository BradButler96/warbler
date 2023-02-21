import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    def test_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user2 = User.signup(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    image_url=None)

            db.session.commit()

            resp = c.get(f"/users/{ user2.id }/following")

            self.assertEqual(resp.status_code, 200)


    def test_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user2 = User.signup(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    image_url=None)

            db.session.commit()

            resp = c.get(f"/users/{ user2.id }/followers")

            self.assertEqual(resp.status_code, 200)


    def test_following_logged_out(self):
        with self.client as c:

            user2 = User.signup(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    image_url=None)

            db.session.commit()

            resp = c.get(f"/users/{ user2.id }/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


    def test_followers_logged_out(self):
        with self.client as c:

            user2 = User.signup(username="testuser2",
                    email="test2@test.com",
                    password="testuser2",
                    image_url=None)

            db.session.commit()

            resp = c.get(f"/users/{ user2.id }/following", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))