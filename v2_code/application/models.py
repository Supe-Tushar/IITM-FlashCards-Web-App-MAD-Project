from .database import db
import time
from flask_security import UserMixin


# --------------------  Users login DB Model  --------------------


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    

    def get_id(self):
        return self.userid

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = password


# --------------------  Deck & Cards DB Model  --------------------


class Deck(db.Model):
    __tablename__ = 'deck'
    deckid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    deckname = db.Column(db.String, unique=False, nullable=False)  # deckname is unique for a user
    deckdesc = db.Column(db.String, nullable=False)
    ltime = db.Column(db.Integer, nullable=True)  # time is stored as a timestamp
    lscore = db.Column(db.Float, nullable=True)
    oscore = db.Column(db.Float, nullable=True)
    userid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    cards = db.relationship('Cards', backref='deck', lazy=True, cascade="all,delete", passive_deletes=True)


class Cards(db.Model):
    __tablename__ = 'cards'
    cardid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question = db.Column(db.String, nullable=False)  # question is unique for given deck
    answer = db.Column(db.String, nullable=False)
    ltime = db.Column(db.Integer, nullable=True)  # time is stored as a timestamp
    lscore = db.Column(db.Float, nullable=True)  # 5: easy, 3: medium, 0: difficult
    deckid = db.Column(db.Integer, db.ForeignKey("deck.deckid", ondelete='CASCADE'), nullable=False)
