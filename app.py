from flask import Flask, flash, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
# get id from session,then retrieve user object from database with peewee query
def load_user(user_id):
    return User.query.get(int(user_id))

#User model and data types.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)

#SignUp Form and fields.
class SignUpForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})
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

#Loginin Form and fields.
class LoginForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#Displayed if user attempts to modify URL to access page without being logged in.
login_manager.login_message = u"You must login to access this page!"

#Home route, displays Buttons routed to Login & Sign Up.
@app.route('/')
def home():
    return render_template('home.html')

#Displays login page and appropriate responses for invalid login attempts.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else: flash('Incorrect Password!')
            return render_template('login.html', form=form)
        else:
            flash('Email not in database!')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


#Logs out user.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Displays signup page and appropriate response if provided email is already in use.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data,username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

#Displays dashboard to logged in user, user uploads image on this page and gets results.
@app.route("/dashboard", methods=["POST","GET"])
@login_required
def dashboard():
    if request.method=='POST':
        file_hold=request.files["image"]
        filename=file_hold.filename
        Path=os.path.join("static/uploads",filename)
        file_hold.save(Path)
        return render_template('index.html',upload_hold=True,img_name=filename)
    return render_template('index.html',upload_hold=False,img_name="")

#Displays plants route to logged in user.
@app.route("/plants")
@login_required
def go_to_plants():
    return render_template("plants.html")

#Displays diseases route to logged in user.
@app.route("/diseases")
@login_required
def go_to_diseases():
    return render_template("diseases.html")

#Displays aboutus route to logged in user.
@app.route("/aboutus")
@login_required
def go_to_aboutus():
    return render_template("aboutus.html")


if __name__ == "__main__":
    #Creates and initalizes database. 
    #Only creates database if database.db is missing,
    #if not the existing database.db will be used.
    db.create_all()
    app.run(port=8000, debug=True)
