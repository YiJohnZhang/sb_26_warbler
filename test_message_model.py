import os;
from unittest import TestCase;
from models import db, connect_db, Message, User;

os.environ['DATABASE_URL'] = "postgresql:///sb_26_warbler_test";

from app import app, CURR_USER_KEY;

db.drop_all();
db.create_all();

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client();
    
        # how do you expect me to write tests for this when there are no message class/instance methods?!?
        