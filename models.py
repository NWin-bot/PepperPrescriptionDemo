from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

#User model and data types.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    hint = db.Column(db.String(20), nullable=False)
    image = db.Column(db.Text)
    since = db.Column(db.Text)
    last = db.Column(db.Text)
    email_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    sessions = db.relationship('Session', backref='user')

#Session model and data types
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text)
    disease = db.Column(db.String(50))
    severity = db.Column(db.Integer)
    image = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#Disease model and data types
class Disease(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    disease = db.Column(db.String(120))
    description = db.Column(db.Text)
    symptom = db.Column(db.Text)
    treatment = db.Column(db.Text)
    image = db.Column(db.Text)