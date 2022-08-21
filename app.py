from flask import Flask;
from flask import request, session, g, render_template, redirect, url_for, flash, jsonify;
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, MessageForm, UserEditForm;
from models import db, connect_db, User, Message, Likes;

import os
from functools import wraps;

# Constants
CURR_USER_KEY = "curr_user";
RETURN_PAGE_KEY = "previous_page";

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///sb_26_warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False;
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False;
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

''' HELPER FUNCTIONS
'''

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def findUserByID(userID):

    selectedUser = User.returnUserByID(userID);

    if not selectedUser:
        print('not!')
        return -1; 
        # gracefully search db so that the user can return to where they came from without the referrer being `None` and the non-existent ID.

    return selectedUser;

''' Before & After Decorators
'''
@app.before_request
def before_request():
    """If we're logged in, add curr user to Flask global."""

    # update current user
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

    # get request path
        # https://stackoverflow.com/questions/39777171/how-to-get-the-previous-url-in-flask
    
    session[RETURN_PAGE_KEY] = request.referrer;
        # need the 200 referrer, not the redirect referrrer

@app.after_request
def after_request(req):
    """Add non-caching headers on every request."""
        
    #   Turn off all caching in Flask: (useful for dev; in production, this kind of stuff is typically handled elsewhere)
    #       https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

''' Custom Decorators
    Define a Custom Decorator: https://medium.com/@nguyenkims/python-decorator-and-flask-3954dd186cda
    Python Documentation: https://docs.python.org/3/library/functools.html#functools.wraps
'''    
# Authentication Decorators

def notLoggedIn_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if g.user:
            return redirect(url_for('index'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def loginRequired_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger");
            return redirect(url_for('index'));
            
        return f(*args, **kwargs);
    
    return wrapper;

def loginOptional_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):


        return f(*args, **kwargs);
    
    return warpper;

def adminAction_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        return f(*args, **kwargs);
    
    return wrapper;

# Helper Decorators


''' ERROR Decorators
'''
@app.errorhandler(404)
def error_404(error):
    '''404: Not Found View'''
    return render_template('errors/error.html', errorCode = 404, previousPath = session[RETURN_PAGE_KEY]), 404;

@app.errorhandler(403)
def error_403(error):
    '''403: Forbidden View'''
    return render_template('errors/error.html', errorCode = 403, previousPath = session[RETURN_PAGE_KEY]), 403;

''' VIEWS
'''
#   Home and Error Page
@app.route('/')
def index():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:

        messages = Message.query.filter(Message.user_id.in_(g.user.listOfUserFollowings())).order_by(Message.timestamp.desc()).limit(100).all();


        return render_template('home.html', messages=messages)
            # source of the 78 queries.

    else:
        return render_template('home.html', anonymous = True);
            # probably could check if not messages? no, in case there are no messages (new account).

#   User Sign-Up/Login/Logout

@app.route('/signup', methods=["GET", "POST"])
@notLoggedIn_decorator
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            # if the username is taken, the database throws and IntegrityError
            form.username.errors = ['Username already taken.'];
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect(url_for('index'));

    else:
        return render_template('users/onboarding.html', form=form,
            onboardingAction = 'signup');


@app.route('/login', methods=["GET", "POST"])
@notLoggedIn_decorator
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('index'));

        flash("Invalid credentials.", 'danger')

    return render_template('users/onboarding.html', form=form,
        onboardingAction = 'login');


@app.route('/logout')
@loginRequired_decorator
def logout():
    """Handle logout of user."""
    
    do_logout();

    return redirect(url_for('index'));


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    # for private user, check if logged in; check if following then show; o.w. redirect to home (UI/landing)

    selectedUser = findUserByID(user_id);
        # so apparently, a query is made for "user_id" by default and if it is a get_or_404 call ._.

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user = selectedUser, messages=messages)


@app.route('/users/<int:user_id>/following')
@loginRequired_decorator
def show_following(user_id):
    """Show list of people this user is following."""

    selectedUser = findUserByID(user_id);

    return render_template('users/following.html', user = selectedUser)


@app.route('/users/<int:user_id>/followers')
@loginRequired_decorator
def users_followers(user_id):
    """Show list of followers of this user."""

    selectedUser = findUserByID(user_id);
    return render_template('users/followers.html', user = selectedUser)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
@loginRequired_decorator
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    followed_user = User.returnUserByID(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(url_for('show_following', user_id = g.user.id));


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
@loginRequired_decorator
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    followed_user = User.returnUserByID(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(url_for('show_following', user_id = g.user.id));


@app.route('/users/profile', methods=["GET", "POST"])
@loginRequired_decorator
def profile():
    """Update profile for current user."""
    
    # print(f'referrer: {session[RETURN_PAGE_KEY]}')

    editUserForm = UserEditForm(**g.user.returnUserInformation());
     
    if editUserForm.validate_on_submit():
        
        if User.authenticate(g.user.username, editUserForm.password.data):

            try:
                
                User.updateUser(g.user, request.form);

            except IntegrityError:

                editUserForm.username.errors = ['Username already taken.'];
                return render_template('users/edit.html', form = editUserForm, 
                    user_id = g.user.id);

            return redirect(url_for('users_show', user_id = g.user.id));

        else:
            
            editUserForm.password.errors = ['Invalid Password. Try again.'];
            return render_template('users/edit.html', form = editUserForm, 
                user_id = g.user.id);
                # is this necessary?

    return render_template('users/edit.html', form = editUserForm, 
        user_id = g.user.id);


@app.route('/users/delete', methods=["POST"])
@loginRequired_decorator
def delete_user():
    """Delete user."""

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect(url_for('signup'));


##############################################################################
# Messages routes:
@app.route('/messages/new', methods=["GET", "POST"])
@loginRequired_decorator
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(url_for('users_show', user_id = g.user.id));

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
@loginRequired_decorator
def messages_destroy(message_id):
    """Delete a message."""
    
    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(url_for('users_show', user_id = g.user.id));

''' User-Likes View

'''
@app.route('/users/add_like/<int:messageID>', methods=["POST"])
@loginRequired_decorator
def toggleMessageLikeView(messageID):
    
    currentUser = g.user;

    Likes.toggleLike(currentUser.id, messageID);

    return redirect(url_for('index'));

@app.route('/users/<int:userID>/likes', methods=['GET'])
@loginRequired_decorator
def usersLikedMessageView(userID):
    
    selectedUser = findUserByID(userID);

    messages = [message.likes_messages for message in Likes.queryLikesByUserID(selectedUser.id)];

    return render_template('users/show.html', user = selectedUser, messages=messages);