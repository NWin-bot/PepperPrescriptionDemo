from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email, EqualTo
from models import User


#SignUp Form and fields.
class SignUpForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=50),Email(message="Invalid, Email Format!")], render_kw={"placeholder": "Email"})
    
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    confirm = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})
    
    hint = StringField(validators=[
                           InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password Hint"})

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
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#ProfileUserUpdate Form and fields.
class ProfileUserUpdateForm(FlaskForm):
    
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    submit = SubmitField('Update')

#ProfilePassUpdate Form and fields.
class ProfilePassUpdateForm(FlaskForm):
    
    password = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    confirm = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField('Update')

#Forgot/Reset password forms and fields.
class EmailForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    
    submit = SubmitField('Submit')

class PasswordForm(FlaskForm):
    password = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    confirm = PasswordField(validators=[
                           InputRequired(), Length(min=8, max=20), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})
    
    submit = SubmitField('Submit')