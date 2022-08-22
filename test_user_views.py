import os;
from unittest import TestCase;
from models import db, connect_db, Message, User;

os.environ['DATABASE_URL'] = "postgresql:///sb_26_warbler_test";
from app import app, CURR_USER_KEY;
app.config['SQLALCHEMY_ECHO'] = False;
app.config['SECRET_KEY'] = 'wtf';

db.drop_all();
db.create_all();

app.config['TESTING'] = True;
app.config['WTF_CSRF_ENABLED'] = False;
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar'];

class TestUserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None);

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test2.com",
                                    password="testuser2",
                                    image_url=None);

        # poor warbler codebase design, adding message is not a database call ._.
            # thankfully I am not using this for more than a few more hours
        db.session.add(Message(text='hi', user_id=1));

        db.session.commit();

    def test_loginDecorator(self):
        '''Tests public's ability to view locked views.'''

        with self.client as client:
            # with client.session_transaction as session:
            #     session[CURR_USER_KEY] = self.testuser.id;

            response = client.get('/logout');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/1/following');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/1/followers');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/follow/2');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/stop-following/2');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/profile');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/delete');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/users/1/likes');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

            response = client.get('/messages/new');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', htmlResponse);

    def test_logoutDecorator(self):
        '''Tests ability to connect to public-only views.'''

        with self.client as client:

            with client.session_transaction as session:
                session[CURR_USER_KEY] = self.testuser.id;

            response = client.get('/signup');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects to user homepage
            self.assertIn('@testuser', htmlResponse);

            response = client.get('/logout');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects to user homepage
            self.assertIn('@testuser', htmlResponse);

            response = client.get('/login');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 302);
                # redirects to user homepage
            self.assertIn('@testuser', htmlResponse);
    
    def test_404Decorator(self):

        with self.client as client:

            with client.session_transaction as session:
                session[CURR_USER_KEY] = self.testuser.id;

            response = client.get('/users/1000');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 404);
            self.assertIn('404', htmlResponse);

            response = client.get('/messages/50');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 404);
            self.assertIn('404', htmlResponse);

            response = client.get('/login');
            htmlResponse = response.get_data(as_text = True);
            self.assertEqual(response.status_code, 404);
            self.assertIn('404', htmlResponse);