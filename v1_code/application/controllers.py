import requests
from flask import render_template, request, redirect, flash, url_for
from flask import current_app as app
from flask_login import login_user, login_required, logout_user
from .models import Users
from .database import db
import json
from datetime import datetime
import os
import random
import time

BASE = 'http://0.0.0.0:8080' #'http://127.0.0.1:5000'

db.create_all()
db.session.commit()

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# ----------------------------- Helper functions --------------------------------


def validUsername(uname):
    valid = list('abcdefghijklmnopqrstuvwxyz0123456789')
    if (len(uname) >= 4) and (len(uname) <= 10):
        for i in uname:
            if i not in valid:
                return False
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


def save_user(obj):
    with open(f"{root}/current_user.json", "w+") as outfile:
        data = {'userid':obj.userid,
                'username':obj.username}
        json.dump(data, outfile, indent=4, sort_keys=False)


# ----------------------------- Authorization Routes --------------------------------


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('uname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # check if username is unique
        user = Users.query.filter_by(username=username).first()
        if user:
            # username is not available
            flash(message='Username is already taken. Please choose different username.', category='error')
        elif validUsername(username):
            if validPassword(password1):
                if password1 == password2:
                    # create new user
                    user = Users(username=username, password=password1)
                    db.session.add(user)
                    db.session.commit()
                    login_user(user, remember=True)
                    save_user(user)
                    flash(message='Account created successfully.', category='success')

                    # # create current user specific db and load it
                    # app.config['SQLALCHEMY_BINDS'] = {
                    # 'db2': f'sqlite:///databases/{current_user.dbname}.sqlite3?charset=utf8'
                    # }
                    # db.create_all(bind=['db2'])

                    return redirect(url_for('dashboard'), 302)
                else:
                    # Passwords did not match
                    flash(message='Passwords did not match. Please enter both passwords correctly.', category='error')
            else:
                # Passwords is not valid
                flash(message='Passwords is not valid. Please enter valid password.', category='error')
        else:
            # Username is not valid
            flash(message='Username is not valid. Please enter valid Username.', category='error')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('password')

        # check if username is unique
        user = Users.query.filter_by(username=username).first()
        if user:
            # username is present in database
            if password == user.password:
                # password matched
                flash(message='Logged in successfully.', category='success')
                login_user(user, remember=True)
                save_user(user)

                # load current user db
                # app.config['SQLALCHEMY_BINDS'] = {
                # 'db2': f'sqlite:///databases/{current_user.dbname}.sqlite3?charset=utf8'
                # }

                return redirect(url_for('dashboard'), 302)
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash(message='Username does not exist in database.', category='error')
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    # logout current user
    logout_user()
    return redirect(url_for('home'))


# ----------------------------- View Routes --------------------------------


@app.template_filter()
def timestamp_to_datetime(timestamp):
    dt = None
    if timestamp:
        dt = str(datetime.fromtimestamp(timestamp))
    return dt


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    last_rev_id = None
    resp = requests.get(BASE + f'/api/deck')
    msg = resp.json()
    decks = []
    if msg.get('category', None) is None:
        deckidList = msg.get('deckidList')
        time_id = []
        for deckid in deckidList:
            resp = requests.get(BASE + f'/api/deck/{deckid}')
            msg = resp.json()
            if msg.get('ltime') is not None:
                time_id.append((msg.get('ltime'), msg.get('deckid')))
            decks.append(msg)
        if time_id:
            time_id = sorted(time_id, key=lambda x: x[0], reverse=True)
            last_rev_id = time_id[0][1]
            for i, deck in enumerate(decks):
                if deck.get('deckid') == last_rev_id:
                    last_rev_id = i+1
                    #print(f"\n\n ind:{i}  deckid:{deck.get('deckid')} \n\n")
                    break
    else:
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
    return render_template('dashboard.html', decks=decks, last_rev_id=last_rev_id)


# -------------------------- Deck ----------------------------


@app.route('/deck/add', methods=['GET', 'POST'])
@login_required
def addDeck():
    if request.method == 'POST':
        # add a deck to database from form inputs
        resp = requests.post(BASE + '/api/deck', request.form)
        msg = resp.json()
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        if msg.get('category') == 'success':
            return redirect(url_for('dashboard'), 302)
        else:
            return render_template('addDeck.html')
    else:
        return render_template('addDeck.html')


@app.route('/deck/<int:deckid>/edit', methods=['GET'])
@login_required
def editDeck(deckid):
    resp = requests.get(BASE + f'/api/deck/{deckid}')
    msg = resp.json()
    if msg.get('category', None) is None:
        # request is successful and deck data has been returned
        deckname = msg.get('deckname')
        cards = msg.get('cards')
        return render_template('editDeck.html', deckname=deckname, cards=cards, deckid=deckid)
    else:
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        return redirect(url_for('dashboard'), 302)


@app.route('/deck/<int:deckid>/edit_desc', methods=['GET', 'POST'])
@login_required
def editDeckDesc(deckid):
    if request.method == 'POST':
        # edit a deck desc to database from form inputs
        resp = requests.put(BASE + f'/api/deck/{deckid}', request.form)
        msg = resp.json()
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        return redirect(url_for('editDeck', deckid=deckid), 302)
    else:
        resp = requests.get(BASE + f'/api/deck/{deckid}')
        msg = resp.json()
        deckname = msg.get('deckname')
        deckdesc = msg.get('deckdesc')
        return render_template('editDeckData.html', deckid=deckid, deckname=deckname, deckdesc=deckdesc)


@app.route('/deck/<int:deckid>/delete', methods=['GET'])
@login_required
def deleteDeck(deckid):
    resp = requests.delete(BASE+ f'/api/deck/{deckid}')
    msg = resp.json()
    flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
    return redirect(url_for('dashboard'), 302)


# -------------------------- Cards ----------------------------


@app.route('/deck/<int:deckid>/card/add', methods=['GET', 'POST'])
@login_required
def addCard(deckid):
    if request.method == 'POST':
        # add a card
        resp = requests.post(BASE + f'/api/deck/{deckid}/card', request.form)
        msg = resp.json()
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        if msg.get('category') == 'success':
            return redirect(url_for('editDeck', deckid=deckid), 302)
    return render_template('addCard.html', deckid=deckid)


@app.route('/deck/<int:deckid>/card/<int:cardid>/edit', methods=['GET', 'POST'])
@login_required
def editCard(deckid, cardid):
    if request.method == 'POST':
        # edit a card
        resp = requests.put(BASE + f'/api/deck/{deckid}/card/{cardid}', request.form)
        msg = resp.json()
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        if msg.get('category') == 'success':
            return redirect(url_for('editDeck', deckid=deckid), 302)

    resp = requests.get(BASE + f'/api/deck/{deckid}/card/{cardid}')
    msg = resp.json()
    if msg.get('category', None) is None:
        # request is successful and card data has been returned
        question = msg.get('question')
        answer = msg.get('answer')
        return render_template('editCard.html', question=question, answer=answer, deckid=deckid, cardid=cardid)
    else:
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        return redirect(url_for('editDeck', deckid=deckid), 302)


@app.route('/deck/<int:deckid>/card/<int:cardid>/delete', methods=['GET'])
@login_required
def deleteCard(deckid, cardid):
    resp = requests.delete(BASE + f'/api/deck/{deckid}/card/{cardid}')
    msg = resp.json()
    flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
    return redirect(url_for('editDeck', deckid=deckid), 302)


# ----------------------------- Review ------------------------------


iter_index = 0
cards_iterator = None
review_score = 0
reviewed_cards = 0

difficulty_to_score = {'Difficult':0, 'Medium':3, 'Easy':5}


@app.route('/deck/<int:deckid>/review', methods=['GET'])
@login_required
def reviewDeck(deckid):
    resp = requests.get(BASE + f'/api/deck/{deckid}')
    msg = resp.json()
    if msg.get('category', None) is None:
        # request is successful and deck data has been returned
        cards = msg.get('cards')
        deckname = msg.get('deckname')
        if len(cards) > 0: # cards are available in that deck
            cards = random.sample(cards, len(cards)) # shuffle cards and store in cards

            global iter_index
            global cards_iterator
            global review_score
            global reviewed_cards

            iter_index = 0
            review_score = 0
            reviewed_cards = 0
            cards_iterator = iter(cards)

            return redirect(url_for('reviewDeckCards', deckid=deckid, index=iter_index), 302)
        else:
            flash(message=f"The deck '{deckname}' does not contain any cards", category='error')
            return redirect(url_for('dashboard'), 302)
    else:
        flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        return redirect(url_for('dashboard'), 302)


@app.route('/deck/<int:deckid>/review/<int:index>', methods=['GET', 'POST'])
@login_required
def reviewDeckCards(deckid, index):
    if request.method == 'POST':
        # get difficulty of a card
        difficulty = request.form.get('difficulty')
        cardid = request.form.get('cardid')
        # store score
        score = difficulty_to_score.get(difficulty)
        resp = requests.put(BASE + f'/api/deck/{deckid}/card/{cardid}', {'ltime':int(time.time())+19800 , 'lscore':score})
        #print('\n\nreview ', score, resp.json(), '\n\n')
        global review_score
        global reviewed_cards

        review_score += score
        reviewed_cards += 1

    global iter_index
    global cards_iterator

    card = next(cards_iterator, 'EndOfTheList')
    iter_index += 1

    if card == 'EndOfTheList':
        # update score
        resp = requests.put(BASE + f'/api/deck/{deckid}',
                            {'ltime': int(time.time())+19800, 'lscore': round((review_score / reviewed_cards),2)})
        msg = resp.json()
        if msg.get('category') == 'success':
            flash(message="Score updated successfully", category=msg.get('category'))
        else:
            flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
        return redirect(url_for('dashboard'), 302)
    else:
        question = card.get('question')
        answer = card.get('answer')
        cardid = card.get('cardid')
        return render_template('review.html',
                               question=question, answer=answer, index=iter_index, deckid=deckid, cardid=cardid)


@app.route('/deck/<int:deckid>/review/<int:index>/abort_review', methods=['GET', 'POST'])
@login_required
def abortReview(deckid, index):
    if request.method == 'POST':
        # get difficulty of a card
        difficulty = request.form.get('difficulty')
        cardid = request.form.get('cardid')
        # store score
        score = difficulty_to_score.get(difficulty)
        resp = requests.put(BASE + f'/api/deck/{deckid}/card/{cardid}', {'ltime':int(time.time())+19800 , 'lscore':score})
        #print('\n\nabort review ', score, resp.json(), '\n\n')
        # update score
        global review_score
        global reviewed_cards

        review_score += score
        reviewed_cards += 1
        #print('\n\n',  review_score/reviewed_cards , '\n\n')
        resp = requests.put(BASE + f'/api/deck/{deckid}',
                            {'ltime':int(time.time())+19800 , 'lscore':round((review_score / reviewed_cards),2)})
        msg = resp.json()
        if msg.get('category') == 'success':
            flash(message="Score updated successfully", category=msg.get('category'))
        else:
            flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
    return redirect(url_for('dashboard'), 302)


# ---------------------- Extra Feature: Import & Export deck ------------------------


@app.route('/deck/<int:deckid>/export', methods=['GET'])
@login_required
def exportDeck(deckid):
    # import required modules
    try:
        import pandas as pd
    except Exception as e:
        print(f'Error in export deck:{e}')
        flash(message='Error occurred while importing pandas module', category='error')
        return redirect(url_for('dashboard'), 302)
    else:
        resp = requests.get(BASE + f'/api/deck/{deckid}')
        msg = resp.json()
        if msg.get('category', None) is None:
            # request is successful and deck data has been returned
            # get deck cards
            deckname = msg.get('deckname')
            cards = msg.get('cards')
            # convert to csv
            cols = ['Srno', 'Question', 'Answer']
            df = pd.DataFrame(columns=cols)
            row = df.shape[0]
            for i, card in enumerate(cards):
                df.at[row, 'Srno'] = i+1
                df.at[row, 'Question'] = card.get('question', 'NA')
                df.at[row, 'Answer'] = card.get('answer', 'NA')
                row += 1
            # save a csv
            df.to_csv(f'{root}/Exports/{deckname}.csv', index=False)
            flash(message='Data exported and saved to Exports directory successfully', category='success')
            return redirect(url_for('dashboard'), 302)
        else:
            flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
            return redirect(url_for('dashboard'), 302)


@app.route('/deck/import', methods=['GET', 'POST'])
@login_required
def importDeck():
    if request.method == 'POST':
        try:
            deckname = request.form.get('deckname')
            deckfile = request.files['file']
            deckfile.save(f'{root}/Imports/{deckfile.filename}')
            import pandas as pd
        except Exception as e:
            print(f'Error in import deck:{e}')
            flash(message='Error occurred while importing a deck', category='error')
            return render_template('importDeck.html')
        else:
            df = pd.read_csv(f'{root}/Imports/{deckfile.filename}')
            resp = requests.post(BASE + '/api/deck', request.form)
            msg = resp.json()
            if msg.get('category') == 'success':
                # deck added and now add cards
                resp = requests.get(BASE + f'/api/deck/{deckname}')
                msg = resp.json()
                if msg.get('category', None) is None:
                    # request is successful and deck data has been returned
                    deckid = msg.get('deckid')
                    total_cards = df.shape[0]
                    error_cards = 0
                    for i in range(df.shape[0]):
                        q = df.at[i, 'Question']
                        a = df.at[i, 'Answer']
                        d = {'question': q, 'answer': a}
                        resp = requests.post(BASE + f'/api/deck/{deckid}/card', d)
                        msg = resp.json()
                        if msg.get('category') != 'success':
                            error_cards += 1
                    if error_cards > 0:
                        flash(message=f"Due to error {error_cards}/{total_cards} cards were not added to deck",
                              category='error')
                    else:
                        flash(message=f"All {total_cards} cards were added to deck",
                              category='success')
                    return redirect(url_for('dashboard'), 302)
                else:
                    flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
                    return render_template('importDeck.html')
            else:
                flash(message=f"Code:{msg.get('status')}  {msg.get('message')}", category=msg.get('category'))
                return render_template('importDeck.html')
    return render_template('importDeck.html')
