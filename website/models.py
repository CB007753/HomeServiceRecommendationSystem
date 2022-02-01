from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    city = db.Column(db.String(150))
    address = db.Column(db.String(300))
    notes = db.relationship('Note')
    hired_user = db.relationship('HiredUser')


class HiredUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    telephone = db.Column(db.String(150))
    work = db.Column(db.String(150))
    status = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))


class HiredHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    telephone = db.Column(db.String(150))
    work = db.Column(db.String(150))
    status = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plumber_id = db.Column(db.Integer, db.ForeignKey('plumbers.id'))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Plumbers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    nic = db.Column(db.String(150))
    address = db.Column(db.String(500))
    city_of_work = db.Column(db.String(150))
    telephone = db.Column(db.Integer)
    occupation = db.Column(db.String(150))
    work = db.Column(db.String(150))
    years_of_experience = db.Column(db.Integer)
    age_group = db.Column(db.String(150))
    nvq_level = db.Column(db.String(150))

