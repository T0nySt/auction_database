from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, DateTimeLocalField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Create Account')


class BidForm(FlaskForm):
    amount = FloatField('Your Bid ($)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Bid must be greater than zero.')
    ])
    submit = SubmitField('Place Bid')


class ItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    starting_price = FloatField('Starting Price ($)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Starting price must be greater than zero.')
    ])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    end_time = DateTimeLocalField('Auction End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('List Item')