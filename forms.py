from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="email is required"), Email(message="Please enter a valid email")])
    password = PasswordField('Password', validators=[DataRequired(message="password is required")])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="email is required"),
        Email(message="Please enter a valid email")
    ])
    username = StringField('Username', validators=[
        DataRequired(message="username is required"),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="password is required")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="password is required"),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError("Username can only contain letters and numbers")

class EditUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    submit = SubmitField('Update Username')

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError("Username can only contain letters and numbers")