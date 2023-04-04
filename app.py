from flask import Flask, flash, render_template, url_for, redirect, request, session
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from models import db, User, Session, Disease
from forms import SignUpForm, LoginForm, ProfileUserUpdateForm, ProfilePassUpdateForm, EmailForm, PasswordForm
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os, csv



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config.from_pyfile('config.cfg')
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
db.app = app
db.init_app(app)

#Creates and initalizes database. 
#Only creates database if database.db is missing,
#if not the existing database.db will be used.
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
# get id from session,then retrieve user object from database with peewee query
def load_user(user_id):
    return User.query.get(int(user_id))

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
                session.permanent = True
                return redirect(url_for('dashboard'))
            else: flash('Password Hint: ' + user.hint)
            return render_template('login.html', form=form)
        else:
            flash('Account, does not exist!')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

#Displays reset password page and accepts email to send reset link to.
@app.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first
        
        #Sending of email confirmation link for password reset
        token = s.dumps(form.email.data, salt='recover-key')
        msg = Message('Pepper Prescription - Password Reset', sender='nickwinter01@gmail.com', recipients=[form.email.data])
        link = url_for('reset_with_token', token=token, _external=True)
        msg.body = 'Hi, welcome to Pepper Prescription, please confirm your email to reset your password {}'.format(link)
        mail.send(msg)
        flash('Check email for password reset link!')
        
    return render_template('reset.html', form=form)

#Clicking of link in email, verifies email and changes state of email confirmation if not already verified.
#New password is accepted and confirmed before being updated.
@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = s.loads(token, salt='recover-key', max_age=1200)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        user.email_confirmed = True

        db.session.add(user)
        db.session.commit()
        flash('Password, Updated!')
        return redirect(url_for('login'))

    return render_template('reset_with_token.html', form=form, token=token)

#Logs out user.
@app.route('/logout')
@login_required
def logout():
    now = datetime.now()
    dt_string = now.strftime("%b/%d/%Y %-I:%M %p")
    current_user.last = dt_string
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

#Displays signup page and appropriate response if provided email is already in use.
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        now = datetime.now()
        dt_string = now.strftime("%b/%d/%Y %-I:%M %p")
        new_user = User(email=form.email.data,username=form.username.data,password=hashed_password,hint=form.hint.data,since=dt_string)
        db.session.add(new_user)
        db.session.commit()

        #Sending of email confirmation link
        token = s.dumps(form.email.data, salt='email-confirm')
        msg = Message('Pepper Prescription - Email Verification', sender='nickwinter01@gmail.com', recipients=[form.email.data])
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'Hi, welcome to Pepper Prescription, please confirm your email {}'.format(link)
        mail.send(msg)
        flash('Check email for confirmation link!')
        return redirect(url_for('login'))
   
    return render_template('signup.html', form=form)

#Clicking of link in email, verifies email and changes state of email confirmation.
#Full site access is granted to user after email confirmation.
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=604800)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    user = User.query.filter_by(email=email).first_or_404()
    user.email_confirmed = True
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('dashboard'))


#Displays dashboard to logged in user, user uploads image on this page and gets results.
#Clicking of submit button in dashboard.html initiates use of route.
@app.route('/dashboard', methods=['POST','GET'])
@login_required
def dashboard():
    if request.method=='POST':
        file_hold=request.files['image']
        filename=file_hold.filename
        #Building of user folder path in static/uploads/email to store submitted jpg files.
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], current_user.email)
        #Creation of user folder path only if it doesn't already exist.
        if not os.path.exists(user_folder):
           os.makedirs(user_folder)
        #--------------------------------------------------------------------------
        #Saving of submitted file to user folder path.
        filename2 = "/".join([current_user.email, filename])
        Path=os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        file_hold.save(Path)
        #--------------------------------------------------------
        userr = User.query.filter_by(email=current_user.email).first()
        now = datetime.now()
        dt_string = now.strftime("%b/%d/%Y %-I:%M %p")
        session = Session(date=dt_string,prediction='',disease='',description='',image=filename,user=userr)
        db.session.add(session)
        db.session.commit()
        return render_template('index.html',upload_hold=True,img_name=filename)
    return render_template('index.html',upload_hold=False,img_name="")


#Displays aboutus route to logged in user.
@app.route('/aboutus')
@login_required
def go_to_aboutus():
    return render_template('aboutus.html')

#Displays history route to logged in user.
@app.route('/history')
@login_required
def go_to_history():
    user = User.query.filter_by(email=current_user.email).first()
    sessionz = Session.query.filter_by(user=user).count()

    page = request.args.get('page', 1, type=int)

    #Enables dynamic pagination.
    #Default value returns full history count (Show All).
    per_page = request.args.get('per_page', sessionz, type=int)

    #Enables hiding of delete button and checkbox when show all is not selected.
    #Default value returns false.
    show = request.args.get('show', False, type=str)
    #---------------------------------------------------------------------------
    
    #Querying of session model to only return the current user sessions by id.
    #The sorting of the sessions in descending order, the most recent upload will be displayed first.
    #The use of pagination to display selected number of post per page.
    sessions = Session.query.filter_by(user=user).order_by(Session.id.desc()).paginate(page=page, per_page=per_page)
    return render_template('history.html',sessions=sessions,num=per_page,show=show)

#Route deletes upload from history page.
#Clicking of delete button in history.html initiates use of route.
@app.route('/delete', methods=['POST','GET'])
@login_required
def delete_from_history():
    if request.method == 'POST': 
     for id in request.form.getlist('mycheckbox'):
      session = Session.query.get(id)
      db.session.delete(session)
      db.session.commit()
     flash('')
    user = User.query.filter_by(email=current_user.email).first()
    sessionz = Session.query.filter_by(user=user).count()
    return redirect(url_for('go_to_history', per_page=sessionz, show=True ))

#Route searches Session database from history page.
#Clicking of search button in history.html initiates use of route.
@app.route('/search', methods=['POST','GET'])
def history_search():
  q = request.args.get('q')
  user = User.query.filter_by(email=current_user.email).first()
  sessionz = Session.query.filter_by(user=user).count()

  if q:
    num = Session.query.filter_by(user=user).filter(Session.image.like('%' + q + '%') | 
                                                    Session.disease.like('%' + q + '%')).count()
    session = Session.query.filter_by(user=user).filter(Session.image.like('%' + q + '%') | 
                                                        Session.disease.like('%' + q + '%')).order_by(Session.id.desc()).paginate(page=1, per_page=num)
  else:
    num = Session.query.filter_by(user=user).count()
    session = Session.query.filter_by(user=user).order_by(Session.id.desc()).paginate(page=1, per_page=num)

  return render_template('history.html',sessions=session,num='',num2=sessionz,show=True)


#Displays profile route to logged in user.
#Clicking of Profile link in profile.html allows user to change profile picture.
@app.route('/profile', methods=['POST','GET'])
@login_required
def go_to_profile():
    show = request.args.get('show', False, type=str)
    if request.method=='POST':
        file_hold=request.files['image']
        filename=file_hold.filename
        #Building of user folder path in static/uploads/email/profile to store submitted jpg files.
        filename2 = "/".join([current_user.email, 'profile'])
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        #Creation of user folder path only if it doesn't already exist.
        if not os.path.exists(user_folder):
               os.makedirs(user_folder)
        #--------------------------------------------------------------------------
        #Saving of submitted file to user folder path.
        filename3 = "/".join([filename2, filename])
        Path=os.path.join(app.config['UPLOAD_FOLDER'], filename3)
        file_hold.save(Path)
        #--------------------------------------------------------
        current_user.image = filename
        db.session.commit()
        flash('Profile Picture, Updated!')
    return render_template('profile.html',show=show)

#Clicking of Username link in profile.html allows user to change username.
@app.route('/username', methods=['POST','GET'])
@login_required
def go_to_profile_username():
    form = ProfileUserUpdateForm()
    show2 = request.args.get('show2', False, type=str)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Username, Updated!')
    return render_template('profile.html',form=form,show2=show2)

#Clicking of Password link in profile.html allows user to change password.
@app.route('/password', methods=['POST','GET'])
@login_required
def go_to_profile_password():
    form = ProfilePassUpdateForm()
    show3 = request.args.get('show3', False, type=str)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        current_user.password = hashed_password
        db.session.commit()
        flash('Password, Updated!')
    return render_template('profile.html',form=form,show3=show3)

#Clicking of Delete link in profile.html allows user to delete account.
@app.route('/deleteaccount')
@login_required
def go_to_profile_deleteaccount():
    user = User.query.filter_by(email=current_user.email).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('signup'))

#Displays diseases route to logged in user.
@app.route('/diseases')
@login_required
def go_to_diseases():
    
    num=Disease.query.count()
    #Only if num is equal 0 to will the csv data be read, this avoids the duplication of data in the Diseases database.
    if num==0:
    #Reading of diseases from csv to display on diseases.html.
     with open('diseases.csv', 'r', encoding="utf-8") as diseases:
       reader = csv.DictReader(diseases)

       for line in reader:
            db.session.add(
        Disease(
            disease=line['Disease'],
            description=line['Description'],
            symptom=line['Symptom'],
            treatment=line['Treatment'],
            image=line['Image']
        )
        )
            
     db.session.commit() #save

    disease = request.args.get('disease',default=None, type=str)

    
    if disease == None:
       diseases = Disease.query.all()
       show=False
    else:
       diseases = Disease.query.filter(Disease.disease.like('%' + disease + '%')).all()
       show=True

    return render_template('diseases.html',diseases=diseases,show=show)




if __name__ == "__main__":
    app.run(port=8000, debug=True)
