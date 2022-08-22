"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Follows(db.Model):
    """Connection of a follower <-> followed_user"""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    # Compund PK is (other_user, user_id)
    #   if user_id is following other_user


class Likes(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key = True
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade'),
        primary_key = True
    )

    likes_user = db.relationship('User', backref=db.backref('user_likes', passive_deletes = True));
        # note SQLALchemy stores related objects in a "InstrumentedList" that is a list of all isntances that match.
        # no-sql may not be necessary!
    likes_messages = db.relationship('Message', backref=db.backref('message_likes', passive_deletes = True));

    def __repr__(self):
        return f'<Likes ({self.user_id}, {self.message_id})';

    @classmethod
    def cleanRequestData(cls, requestData):

        mutableRequestData = dict(requestData);

        if mutableRequestData.get('csrf_token'):
            mutableRequestData.pop('csrf_token');

    @classmethod
    def toggleLike(cls, userID, messageID):

        selectedLike = cls.query.get((userID, messageID));
            # how to search a composite key
            # interesting I was debugging `.get_or_404() and because it returned `None`, it automatically yielded 404.`

        print(selectedLike)

        if not selectedLike:
            # add to db.
            db.session.add(cls(user_id = userID, message_id = messageID));
            db.session.commit();
            return;
        
        db.session.delete(selectedLike);
            # how to query composite keys: https://stackoverflow.com/a/62333875
        db.session.commit();
        return;
    
    @classmethod
    def queryLikesByUserID(cls, userID):
        return cls.query.filter(cls.user_id == userID).all();
    
    @classmethod
    def queryLikesByMessageID(cls, messageID):
        return cls.query.filter(cls.message_id == messageID).all();

    # Jinja filters can take care of this.
    # @classmethod
    # def returnLikeCountByUserID(cls, userID):
        
    #     userLikes = cls.queryLikesByUserID(userID);
    #     return len(userLikes);

    # @classmethod
    # def returnLikeCountByMessageID(cls, messageID):
        
    #     messageLikes = cls.queryLikesByMessageID(messageID);
    #     return len(messageLikes);


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    messages = db.relationship('Message')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    likes = db.relationship(
        'Message',
        secondary="likes"
    )

    def __repr__(self):
        return f"<User {self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_user`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    def returnUserInformation(self):
        '''Returns user information in the database except `id` and `password`.'''

        returnedUserInformation = dict(vars(self));
            # shallow copy: this caused "AttributeError: _sa_intance_state not found for 1 hour ._."

       # remove overhead
        if returnedUserInformation.get('_sa_instance_state'):
            returnedUserInformation.pop('_sa_instance_state');

        if returnedUserInformation.get('id'):
            returnedUserInformation.pop('id');
        
        if returnedUserInformation.get('password'):
            returnedUserInformation.pop('password');

        return returnedUserInformation;


    def listOfUserFollowings(self):
        '''Return a list of users, `otherUsers`, the account user, `referenceUser`, is followed by.'''

        userFollowingList = self.following;
        userFollowingListID = [user.id for user in userFollowingList];

        return userFollowingListID;

    # def recentMessages(self):

    #     return Message.query.filter(Message.user_id.in_(self.listOfUserFollowings())).order_by(Message.timestamp.desc()).limit(100).all();

    @classmethod
    def cleanRequestData(cls, requestData):
        
        mutableRequestData = dict(requestData);

        if mutableRequestData.get('csrf_token'):
            mutableRequestData.pop('csrf_token');
        
        if mutableRequestData.get('id'):    # prevent user from changing their own id
            mutableRequestData.pop('id');

        if mutableRequestData.get('password'):  # do not change password
            mutableRequestData.pop('password');

        return mutableRequestData;

    @classmethod
    def returnUserByID(cls, userID):
        return cls.query.get_or_404(userID);

    @classmethod
    def updateUser(cls, userObject, requestData):

        cleanedRequestData = User.cleanRequestData(requestData);

        print(cleanedRequestData);

        db.session.query(User).filter(User.id==userObject.id).update(cleanedRequestData)
        db.session.commit();

        return;

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False;

class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

    # @classmethod
    # def fetchFollowedRecent100Warbles(cls, userID):
    #     # messages = (Message
    #     #             .query
    #     #             .order_by(Message.timestamp.desc())
    #     #             .limit(100)
    #     #             .all())
    #     # listOfFollowing = User.
    #     return cls.query.filter_by(cls.user_id.in_(listOfFollowing)).order_by(cls.timestamp.desc()).limit(100).all();


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
