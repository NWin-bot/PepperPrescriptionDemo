from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from models import User


#SignUp Form and fields.
class SignUpForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20),Email(message="Invalid Email!")], render_kw={"placeholder": "Email"})
    
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Sign Up')
    
    #Email validation, prevents duplicate emails.
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'This email is already in use!')

#Login Form and fields.
class LoginForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')