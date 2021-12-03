from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    pwd = db.Column(db.String(60))
    clientname = db.Column(db.String(80))
    key = db.Column(db.String(32))