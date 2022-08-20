from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddForm(LoginForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')

class UserEditForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()]);
        # note; pk is id, and assignment specs say to allow changing the username.
    email = StringField('E-mail', validators=[DataRequired(), Email()]);
    image_url = StringField('(Optional) Image URL');
    header_image_url = StringField('(Optional) Image URL');
    bio = StringField();

    passwordConfirmation = PasswordField('Password', validators=[DataRequired()]);