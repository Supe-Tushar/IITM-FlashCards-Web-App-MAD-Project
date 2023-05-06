# --------------------  Imports  --------------------

import os, json, time, requests, jwt, re
from datetime import datetime, timedelta
from functools import wraps
import random

from .models import Users, Deck, Cards
from .database import db
from .errors import *
from .redis_cache import myRedis

from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, make_response
from flask import current_app as app

#from flask_login import login_user, login_required, logout_user
#from flask_security import auth_required

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# --------------------  Helper functions  --------------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # try:token = json.loads(request.get_json()).get('token')
            token = request.headers.get('token')
            #print('Token: ', token)
            #data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            token_redis = myRedis.get('token').decode("utf-8")
            #print(f'\n\ntoken: {token}\nData: {data}\n t2:{t2}\n\n')
            if token != token_redis:
                raise TokenNotMatch('Token didnt match.')
        except Exception as e :
            print("Token required error: ", e)
            return {'category':'error', 'message':'Token is missing or invalid'}, 403
        return f(*args, **kwargs)
    return decorated


def save_user(obj):
    data = {'userid': obj.userid,
            'username': obj.username,
            'useremail': obj.email}
    # with open(f"{root}/current_user.json", "w+") as outfile:
        # json.dump(data, outfile, indent=4, sort_keys=False)
    myRedis.set('current_user', json.dumps(data))


def load_user():
    # with open(f"{root}/current_user.json", "r") as file:
        # data = json.load(file)
        # return data['userid']
    return json.loads(myRedis.get('current_user').decode("utf-8"))['userid']


def card_object_to_dict(obj):
    data = {'cardid': obj.cardid,
            'question': obj.question,
            'answer': obj.answer,
            'ltime': obj.ltime,
            'lscore': obj.lscore,
            'deckid': obj.deckid}
    return data


def deck_object_to_dict(obj):
    cards = []
    if len(obj.cards) > 0:
        for card in obj.cards:
            cards.append(card_object_to_dict(card))
    data = {'deckid': obj.deckid,
            'deckname': obj.deckname,
            'deckdesc': obj.deckdesc,
            'ltime': obj.ltime,
            'lscore': obj.lscore,
            'oscore': obj.oscore,
            'usedid': obj.userid,
            'cards': cards}
    return data
    
    
def user_object_to_dict(obj):
    users = []
    for user in obj:
        data = {'username': user.username,
                'useremail': user.email}
        users.append(data)
    return users


def validUsername(uname):
    valid = list('abcdefghijklmnopqrstuvwxyz0123456789')
    if (len(uname) >= 4) and (len(uname) <= 10):
        for i in uname:
            if i not in valid:
                return False
        return True
    else:
        return False


def validUseremail(uemail):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (re.search(regex, uemail)):
        return True
    else:
        return False


def validPassword(pswd):
    valid = list('abcdefghijklmnopqrstuvwxyz0123456789')
    if (len(pswd) >= 4) and (len(pswd) <= 10):
        for i in pswd:
            if i not in valid:
                return False
        return True
    else:
        return False


# --------------------  Auth API  --------------------

class SignupAPI(Resource):
    def post(self):
        try:
            form = request.get_json()
            username = form.get('uname')
            useremail = form.get('uemail')
            password1 = form.get('password1')
            password2 = form.get('password2')
        except Exception as e:
            print(f'Error: {e}')
            raise InternalServerError
        else:
            # check if username is unique
            user = Users.query.filter_by(username=username).first()
            if user:
                # username is present in database i.e its not unique
                return {'message': 'Username is already taken. Please choose different username.',
                        'category': 'error'}, 409
            elif validUsername(username) :
                if validUseremail(useremail):
                    if validPassword(password1):
                        if password1 == password2:
                            # create new user
                            user = Users(username=username, password=password1, email=useremail)
                            db.session.add(user)
                            db.session.commit()
                            # login_user(user, remember=True)
                            save_user(user)
                            user = Users.query.filter_by(username=username).first()
                            
                            all_users = Users.query.all()
                            all_users = user_object_to_dict(all_users)
                            print(f'all_users : {all_users}')
                            myRedis.set('all_users', json.dumps(all_users)) 
                            
                            return {'message': 'Account created successfully.', 'category': 'success',
                                    'userid': user.userid}, 200
                        else:
                            # Passwords did not match
                            return {'message': 'Passwords did not match. Please enter both passwords correctly.',
                                    'category': 'error'}, 400
                    else:
                        # Passwords is not valid
                        return {'message': 'Passwords is not valid. Please enter valid password.', 'category': 'error'}, 400
                else:
                    # Email is not valid
                    return {'message': 'Email is not valid. Please enter valid Email.',
                            'category': 'error'}, 400
            else:
                # Username is not valid
                return {'message': 'Username is not valid. Please enter valid Username.', 'category': 'error'}, 400


class LoginAPI(Resource):
    def post(self):
        token = ''
        try:
            form = request.get_json()
            useremail = form.get('uemail')
            password = form.get('password')
        except Exception as e:
            print(f'Error: {e}')
            raise InternalServerError
        else:
            if validUseremail(useremail) and validPassword(password):
                # check if username is unique
                user = Users.query.filter_by(email=useremail).first()
                if user:
                    # username is present in database
                    if password == user.password:
                        # create new user
                        #login_user(user, remember=True)
                        save_user(user)
                        
                        all_users = Users.query.all()
                        all_users = user_object_to_dict(all_users)
                        print(f'all_users : {all_users}')
                        myRedis.set('all_users', json.dumps(all_users)) 
                            
                            
                        # Generate jwt auth token
                        valid_dur = 300 #seconds
                        token = jwt.encode({'email':useremail,
                                            'exp':datetime.now()+timedelta(minutes=0,seconds=valid_dur)},
                                           app.config['SECRET_KEY'], algorithm="HS256")
                        # token is in string format
                        print('Generate token: ', token)
                        myRedis.setex('token', timedelta(minutes=0, seconds=valid_dur), str(token)) #set with expiry

                        return {'message': 'Logged in successfully.', 'category': 'success',
                                'userid': user.userid, "token": token}, 200
                    else:
                        # Passwords did not match
                        return {'message': 'Passwords did not match.', 'category': 'error'}, 400
                else:
                    # Username is not valid
                    return {'message': 'Username does not exist', 'category': 'error'}, 404
            else:
                # Email or password is not valid
                return {'message': 'Email or password is not valid', 'category': 'error'}, 400



# --------------------  Deck API  --------------------


class DeckAPI(Resource):
    @token_required
    def get(self, deckid=None, deckname=None):
        if deckid is not None:
            if (type(deckid) is int) and (deckid > 0):
                try:
                    deck = Deck.query.filter_by(deckid=deckid, userid=load_user()).first()
                except Exception as e:
                    print(f'Error: {e}')
                    raise InternalServerError
                else:
                    if deck:
                        # deckid exists
                        return make_response(jsonify(deck_object_to_dict(deck)), 200)
                    else:
                        # deckid does not exist
                        raise NotFoundError(status_msg='Deck for the given deckid does not exist')
            else:
                raise InvalidDataError(status_msg='Input deckid must be positive integer')
        if deckname is not None:
            # requesting deckid from deck name
            try:
                deck = Deck.query.filter_by(deckname=deckname, userid=load_user()).first()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if deck:
                    # deck for given deckname exists
                    return make_response(jsonify(deck_object_to_dict(deck)), 200)
                else:
                    # deck for given deckname does not exist
                    raise NotFoundError(status_msg='Deck for the given deckname does not exist')
        if deckid is None and deckname is None:
            # for current user get all deckid's
            try:
                decks = Deck.query.filter_by(userid=load_user()).all()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if decks:
                    deckidList = []
                    for deck in decks:
                        deckidList.append(deck.deckid)
                    return make_response(jsonify({'deckidList': deckidList, 'category':'success'}), 200)
                else:
                    # decks for current user not exist
                    raise NotFoundError(status_msg='Deck for current user does not exist')

    @token_required
    def post(self):
        # addDeck importDeck Html
        try:
            try:
                form = request.get_json()
                deckname = form.get('deckname')
                deckdesc = form.get('deckdesc')
                deck = Deck.query.filter_by(deckname=deckname, userid=load_user()).first()
            except:
                try:
                    form = request.form
                    deckname = form.get('deckname')
                    deckdesc = form.get('deckdesc')
                    deck = Deck.query.filter_by(deckname=deckname, userid=load_user()).first()
                except Exception as e:
                    print(f'Error: {e}')
                    raise InternalServerError
        except Exception as e:
            print(f'Error: {e}')
            raise InternalServerError
        else:
            if type(deckname) is str and type(deckdesc) is str:  # by default inputs are string
                if deck:
                    # deck name already exists
                    raise AlreadyExistError(status_msg='Deck name already exists. Choose different deck name')
                else:
                    # deckid does not exist
                    deck = Deck(deckname=deckname, deckdesc=deckdesc, userid=load_user())
                    db.session.add(deck)
                    db.session.commit()
                    raise Success_201(status_msg='Deck successfully added to database')
            else:
                raise InvalidDataError(status_msg='Deck name and deck description must be string')

    @token_required
    def put(self, deckid):
        # editDeckData Html
        if (type(deckid) is int) and (deckid > 0):
            try:
                deck = Deck.query.filter_by(deckid=deckid, userid=load_user()).first()
                form = request.get_json()
                deckdesc = form.get('deckdesc', None)
                ltime = form.get('ltime', None)
                lscore = form.get('lscore', None)
                # oscore = form.get('oscore', None)
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if deck:
                    # deckid exists
                    if deckdesc is None:
                        # We are updating last reviewed time and scores
                        try:
                            ltime = int(ltime)
                            lscore = float(lscore)
                        except:
                            raise InvalidDataError(status_msg='Input data is invalid')
                        else:
                            deck.ltime = ltime  # last reviewed time
                            deck.lscore = lscore  # last reviewed time
                            oscore = deck.oscore  # current overall score
                            if oscore is None:
                                deck.oscore = lscore
                            else:
                                deck.oscore = round((oscore + lscore) / 2, 2)
                            db.session.commit()
                            raise Success_200(status_msg='Last reviewed time and scores successfully updated')
                    else:
                        # deckname can not be edited because it must be unique
                        deck.deckdesc = deckdesc
                        db.session.commit()
                        raise Success_200(status_msg='Deck description successfully edited')
                else:
                    # deckid does not exist
                    raise NotFoundError(status_msg='Deck for the given deckid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid must be positive integer')

    @token_required
    def delete(self, deckid):
        if (type(deckid) is int) and (deckid > 0):
            try:
                deck = Deck.query.filter_by(deckid=deckid, userid=load_user()).first()
                cards = Cards.query.filter_by(deckid=deckid).all()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if deck:
                    # deckid exists
                    if len(cards) > 0:
                        for card in cards:
                            try:
                                # card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
                                db.session.delete(card)
                                db.session.commit()
                                print("Card deleted.")
                            except Exception as e:
                                print(f'Error in deleting cards: {e}')
                    # delete is  set to cascade. Deleting a deck will automatically delete all cards associated with it.
                    # print('\n\n', deck.cards, '\n\n')
                    db.session.delete(deck)
                    db.session.commit()
                    # print('\n\n', Cards.query.filter_by(deckid=deckid).all(), '\n\n')
                    raise Success_200(status_msg='Deck and respective cards successfully deleted')
                else:
                    # deckid does not exist
                    raise NotFoundError(status_msg='Deck for the given deckid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid must be positive integer')


# --------------------  Cards API  --------------------


class CardAPI(Resource):
    @token_required
    def get(self, deckid, cardid):
        if (type(deckid) is int) and (deckid > 0) and (type(cardid) is int) and (cardid > 0):
            try:
                card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if card:
                    # cardid exists
                    return make_response(jsonify(card_object_to_dict(card)), 200)
                else:
                    # cardid does not exist
                    raise NotFoundError(status_msg='Card for the given deckid and cardid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid and cardid must be positive integer')

    @token_required
    def post(self, deckid):
        # addCard Html
        if (type(deckid) is int) and (deckid > 0):
            try:
                try:
                    form = request.get_json()
                    question = form.get('question')
                    answer = form.get('answer')
                    card = Cards.query.filter_by(deckid=deckid, question=question).first()
                except:
                    try:
                        form = request.form
                        question = form.get('question')
                        answer = form.get('answer')
                        card = Cards.query.filter_by(deckid=deckid, question=question).first()
                    except Exception as e:
                        print(f'Error: {e}')
                        raise InternalServerError
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if card:
                    # card exists
                    raise AlreadyExistError(
                        status_msg='For the given question a card already exists in the deck. Question for a deck must be unique')
                else:
                    # card does not exist
                    card = Cards(question=question, answer=answer, deckid=deckid)
                    db.session.add(card)
                    db.session.commit()
                    raise Success_201(status_msg='Card successfully added to deck')
        else:
            raise InvalidDataError(status_msg='Input deckid must be positive integer')

    @token_required
    def put(self, deckid, cardid):
        # editCard Html
        if (type(deckid) is int) and (deckid > 0) and (type(cardid) is int) and (cardid > 0):
            form = request.get_json()
            question = form.get('question', None)
            if question is None:
                # we are updating only last reviewed time and score of a card
                try:
                    card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
                    ltime = form.get('ltime', None)
                    lscore = form.get('lscore', None)
                except Exception as e:
                    print(f'Error: {e}')
                    raise InternalServerError
                else:
                    if card:
                        # card for given deckid and cardid exists
                        try:
                            ltime = int(ltime)
                            lscore = float(lscore)
                        except:
                            raise InvalidDataError(status_msg='Input data is invalid')
                        else:
                            card.ltime = ltime  # last reviewed time
                            card.lscore = lscore  # last reviewed time
                            db.session.commit()
                            raise Success_200(
                                status_msg='Last reviewed time and scores for a card successfully updated')
                    else:
                        # card does not exist
                        raise NotFoundError(status_msg='Card for the given deckid and cardid does not exist')
            else:
                try:
                    answer = form.get('answer')
                    card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
                    cards = Cards.query.filter_by(deckid=deckid,
                                                  question=question).all()  # question must be unique so len(cards) should be 0 or 1
                except Exception as e:
                    print(f'Error: {e}')
                    raise InternalServerError
                else:
                    if card:
                        if ((card.question == question) and (len(cards) != 1)) or (
                                (card.question != question) and (len(cards) != 0)):
                            raise AlreadyExistError(status_msg='Card with same question already exist')
                        else:
                            # cardid exists and question is unique
                            card.question = question
                            card.answer = answer
                            db.session.commit()
                            raise Success_200(status_msg='Card successfully edited')
                    else:
                        # card does not exist
                        raise NotFoundError(status_msg='Card for given cardid and deckid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid and cardid must be positive integer')

    @token_required
    def delete(self, deckid, cardid):
        print("Inside delete card", deckid, cardid)
        if (type(deckid) is int) and (deckid > 0) and (type(cardid) is int) and (cardid > 0):
            try:
                card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if card:
                    # card exists
                    db.session.delete(card)
                    db.session.commit()
                    raise Success_200(status_msg='Card successfully deleted')
                else:
                    # card does not exist
                    raise NotFoundError(status_msg='Card for given cardid and deckid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid and cardid must be positive integer')
