from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

#User model and data types.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    sessions = db.relationship('Session', backref='user')

#Session model and data types
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text)
    prediction = db.Column(db.String(50))
    disease = db.Column(db.String(50))
    treatment = db.Column(db.Text)
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