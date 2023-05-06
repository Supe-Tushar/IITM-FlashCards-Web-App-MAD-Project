# --------------------  Imports  --------------------
import json
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, make_response
from .models import Deck, Cards
from .database import db
from .errors import *
import os

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# --------------------  Helper functions  --------------------


def load_user():
    with open(f"{root}/current_user.json", "r") as file:
        data = json.load(file)
        return data['userid']


def card_object_to_dict(obj):
    data = {'cardid':obj.cardid,
            'question':obj.question,
            'answer': obj.answer,
            'ltime' : obj.ltime,
            'lscore' : obj.lscore,
            'deckid':obj.deckid}
    return data


def deck_object_to_dict(obj):
    cards = []
    if len(obj.cards) > 0:
        for card in obj.cards:
            cards.append(card_object_to_dict(card))
    data = {'deckid' : obj.deckid,
            'deckname' : obj.deckname,
            'deckdesc' : obj.deckdesc,
            'ltime' : obj.ltime,
            'lscore' : obj.lscore,
            'oscore' : obj.oscore,
            'usedid' : obj.userid,
            'cards' : cards}
    return data


# --------------------  Deck API  --------------------


class DeckAPI(Resource):
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
                    return make_response(jsonify({'deckidList':deckidList}), 200)
                else:
                    # decks for current user not exist
                    raise NotFoundError(status_msg='Deck for current user does not exist')

    def post(self):
        # addDeck importDeck Html
        try:
            deckname = request.form.get('deckname')
            deckdesc = request.form.get('deckdesc')
            deck = Deck.query.filter_by(deckname=deckname, userid=load_user()).first()
        except Exception as e:
            print(f'Error: {e}')
            raise InternalServerError
        else:
            if type(deckname) is str and type(deckdesc) is str: # by default inputs are string
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

    def put(self, deckid):
        # editDeckData Html
        if (type(deckid) is int) and (deckid > 0):
            try:
                deck = Deck.query.filter_by(deckid=deckid, userid=load_user()).first()
                deckdesc = request.form.get('deckdesc', None)
                ltime = request.form.get('ltime', None)
                lscore = request.form.get('lscore', None)
                #oscore = request.form.get('oscore', None)
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
                            deck.ltime = ltime # last reviewed time
                            deck.lscore = lscore # last reviewed time
                            oscore = deck.oscore # current overall score
                            if oscore is None:
                                deck.oscore = lscore
                            else:
                                deck.oscore = round((oscore + lscore)/2, 2)
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

    def delete(self, deckid):
        if (type(deckid) is int) and (deckid > 0):
            try:
                deck = Deck.query.filter_by(deckid=deckid, userid=load_user()).first()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if deck:
                    # deckid exists
                    # delete is  set to cascade. Deleting a deck will automatically delete all cards associated with it.
                    #print('\n\n', deck.cards, '\n\n')
                    db.session.delete(deck)
                    db.session.commit()
                    #print('\n\n', Cards.query.filter_by(deckid=deckid).all(), '\n\n')
                    raise Success_200(status_msg='Deck and respective cards successfully deleted')
                else:
                    # deckid does not exist
                    raise NotFoundError(status_msg='Deck for the given deckid does not exist')
        else:
            raise InvalidDataError(status_msg='Input deckid must be positive integer')


# --------------------  Cards API  --------------------


class CardAPI(Resource):
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

    def post(self, deckid):
        # addCard Html
        if (type(deckid) is int) and (deckid > 0):
            try:
                question = request.form.get('question')
                answer = request.form.get('answer')
                card = Cards.query.filter_by(deckid=deckid, question=question).first()
            except Exception as e:
                print(f'Error: {e}')
                raise InternalServerError
            else:
                if card:
                    # card exists
                    raise AlreadyExistError(status_msg='For the given question a card already exists in the deck. Question for a deck must be unique')
                else:
                    # card does not exist
                    card = Cards(question=question, answer=answer, deckid=deckid)
                    db.session.add(card)
                    db.session.commit()
                    raise Success_201(status_msg='Card successfully added to deck')
        else:
            raise InvalidDataError(status_msg='Input deckid must be positive integer')

    def put(self, deckid, cardid):
        # editCard Html
        if (type(deckid) is int) and (deckid > 0) and (type(cardid) is int) and (cardid > 0):
            question = request.form.get('question', None)
            if question is None:
                # we are updating only last reviewed time and score of a card
                try:
                    card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
                    ltime = request.form.get('ltime', None)
                    lscore = request.form.get('lscore', None)
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
                            raise Success_200(status_msg='Last reviewed time and scores for a card successfully updated')
                    else:
                        # card does not exist
                        raise NotFoundError(status_msg='Card for the given deckid and cardid does not exist')
            else:
                try:
                    answer = request.form.get('answer')
                    card = Cards.query.filter_by(deckid=deckid, cardid=cardid).first()
                    cards = Cards.query.filter_by(deckid=deckid, question=question).all()  # question must be unique so len(cards) should be 0 or 1
                except Exception as e:
                    print(f'Error: {e}')
                    raise InternalServerError
                else:
                    if card:
                        if ((card.question == question) and (len(cards) != 1)) or ((card.question != question) and (len(cards) != 0)):
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

    def delete(self, deckid, cardid):
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
