from weasyprint import HTML
from jinja2 import Template
from flask import render_template, request, redirect, flash, url_for
import pandas as pd
import requests
from datetime import datetime, timedelta
import os, random, time, json

from celery import Celery
from celery.schedules import crontab
celery = Celery('myapp', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')


# monthly report: at 8 am on 1st day of monthly
# daily alert : at 8 am daily
class celeryConfig():
    CELERYBEAT_SCHEDULE = {
      'every_month_report': {
        'task': 'application.workers.report_generate_async',
        'schedule': crontab(day_of_month=1, hour=8,minute=0),
        'args': ('',{}),
        'options': {
            'expires': 15.0,
            }
        },
        'every_day_alert': {
        'task': 'application.workers.send_alert_async',
        'schedule': crontab(hour=8,minute=0),
        'args': ({}),
        'options': {
            'expires': 15.0,
            }
        }
    }
    
    
celery.config_from_object(celeryConfig())


import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from email.mime.application import MIMEApplication

SMTP_SERVER_HOST = '127.0.0.1'
SMTP_SERVER_PORT = 1025
SENDER_NAME = 'Tushar'
SENDER_ADDRESS = "xxx"
SENDER_PASSWORD = "xxx" #os.environ.get('SENDER_PASSWORD')


BASE = 'http://127.0.0.1:5000'  # 'http://0.0.0.0:8080'

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# this root is at app.py level


def check_internet():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        return False


def send_email(to, sub='', msg='', any_attach=False, filesList=[], content='html'):
    message = MIMEMultipart()
    message['From'] = SENDER_ADDRESS
    message['To'] = to
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = sub
    message.attach(MIMEText(msg, content))

    if any_attach:
        if len(filesList) > 0:
            for file in filesList: #complete file path
                filename = os.path.basename(file)
                with open(file, "rb") as ff:
                    part = MIMEApplication(ff.read(), Name=filename)
                part['Content-Disposition'] = 'attachment; filename="%s"' % filename
                message.attach(part)

    if check_internet():
        try:
            # smtp = smtplib.SMTP('smtp.gmail.com', 587) # to actual mail address
            smtp = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)  # to mailhog
            smtp.login(SENDER_ADDRESS, SENDER_PASSWORD)
        except Exception as e:
            return {'category':'error','message':str(e)}, 500
        else:
            smtp.send_message(msg=message)
            smtp.quit()
            return {'category': 'success', 'message': 'Mail sent'}, 200
    else:
        return {'category':'error','message':'No internet connection'}, 500



def format_msg(filepath, data={}):
    with open(filepath) as file:
        template = Template(file.read())
    return template.render(data=data)


def generate_N_send_pdf(useremail, username, data={}):
    data.update({'useremail':useremail, 'username':username})
    message = format_msg(os.path.join(root, 'templates', 'report.html'), data=data)
    html = HTML(string=message)
    x = datetime.now()
    y = datetime.timestamp(x)
    name = f'Report_{int(y)}_{x.strftime("%m-%d-%Y_%a_%H-%M-%S")}.pdf'
    filename = os.path.join(root, 'Exports', name)
    html.write_pdf(target=filename)

    x, _ = send_email(useremail,
                                sub='FlashCards - Progress Report',
                                msg=format_msg(os.path.join(root, 'templates', 'report_mail.html'),
                                               data={'username': username}),
                                any_attach=True,
                                filesList=[os.path.join(root, 'Exports', name)])
    return x


def send_exported_csv(useremail, username, csvname):
    x,_ = send_email(useremail,
                        sub='FlashCards - Exported Deck as CSV',
                        msg=format_msg(os.path.join(root, 'templates', 'export_deck.html'),
                                       data={'username': username}),
                        any_attach=True,
                        filesList=[os.path.join(root, 'Exports', f'{csvname}.csv')])
    return x


#------------------------------ Celery Tasks ------------------------------



googleChatLink =  "xxx" # os.environ.get('googleChatLink')


@celery.task()
def send_alert_async(all_users):
    print("inside send alert async ")
    try:
        print(f"inside worker: all users : {all_users}")
        for user in all_users:
            r = requests.post(googleChatLink, data=json.dumps({'text':f'Alert for {user["username"]}: Visit "FlashCards" app and start practicing. Link:"http://127.0.0.1:5000"'}))
    
            x, _ = send_email(user["useremail"],
                                sub='Alert: Practice flashcards',
                                msg=format_msg(os.path.join(root, 'templates', 'alerts.html'),
                                data={'username': user["username"]}))
                                       
        return {'message': 'Notification sent', 'category': 'success'}, 200
    except Exception as e:
        return {'message': f'Backend error in notifying. Didnt get users. {e}\nTry again', 'category': 'error'}, 500



@celery.task()
def report_generate_async(token, current_user):
    try:
        useremail = current_user['useremail']
        username = current_user['username']
        
        resp = requests.get(BASE + f'/api/deck', headers={'token':token})
        msg = resp.json()
        decks = []
        cards = []
        print('msg_1: ', msg, type(msg))
        
        if msg.get('category') == 'success':
            for deckid in msg['deckidList']:
                resp = requests.get(BASE + f'/api/deck/{deckid}', headers={'token':token})
                msg = resp.json()
                print('msg_2: ', msg, type(msg))
                
                deck = {}
                if msg.get('category') is None:
                    # deck data received
                    if msg['ltime']:
                        msg['ltime'] = datetime.fromtimestamp(int(msg['ltime'])) 
                    decks.append(msg)
                    for card in msg['cards']:
                        card['deckname'] = msg['deckname']
                        if card['ltime']:
                            card['ltime'] = datetime.fromtimestamp(int(card['ltime'])) 
                        cards.append(card)
            print('deck data: ', {'decks':decks, 'cards':cards})
            report_mail_job = generate_N_send_pdf(useremail=useremail, username=username, data={'decks':decks, 'cards':cards})
            if report_mail_job['category'] == 'success':
                return {'message': 'Data exported and successfully sent to registered email id', 'category': 'success'}, 200
            else:
                return report_mail_job, 500
        else:
            return {'message': msg['message'], 'category': 'error'}, 500
    except Exception as e:
        print(f'Error in report generation :{e}')
        return {'message': 'Backend error. Try again', 'category': 'error'}, 500

       
@celery.task()
def export_deck_async(deckid, token, current_user):
    print("\n\nInside export async")
    try:
        resp = requests.get(BASE + f'/api/deck/{deckid}', headers={'token':token})
        msg = resp.json()
    except Exception as e:
        print(f'Error in exporting deck deck:{e}')
        return {'message': 'Backend error. Try again', 'category': 'error'}, 500
    else:
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
                df.at[row, 'Srno'] = i + 1
                df.at[row, 'Question'] = card.get('question', 'NA')
                df.at[row, 'Answer'] = card.get('answer', 'NA')
                row += 1
            # save a csv
            df.to_csv(f'{root}/Exports/{deckname}.csv', index=False)

            # send mail and attach csv
            useremail = current_user['useremail']
            username = current_user['username']
            export_mail_job = send_exported_csv(useremail=useremail, username=username, csvname=deckname)
            if export_mail_job['category'] == 'success':
                return {'message': 'Data exported and successfully sent to registered email id', 'category': 'success'}, 200
            else:
                return export_mail_job, 500
        else:
            return {'message': msg.get('message'), 'category': 'error'}, 400


@celery.task()
def import_deck_async(filename, deckname, deckdesc, token):
    print("Inside import deck async")
    try:
        resp = requests.post(BASE + '/api/deck', {'deckname': deckname, 'deckdesc': deckdesc}, headers={'token':token})
        msg = resp.json()
        df = pd.read_csv(f'{root}/Imports/{filename}')
        # add cards
        resp = requests.get(BASE + f'/api/deck/{deckname}', headers={'token':token})
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
                resp = requests.post(BASE + f'/api/deck/{deckid}/card', d , headers={'token':token})
                msg = resp.json()
                if msg.get('category') != 'success':
                    error_cards += 1
            if error_cards > 0:
                return {'message': f"Due to error {error_cards}/{total_cards} cards were not added to deck",
                        'category': 'error'}, 400
            return {'message': f'All {total_cards} cards were added to deck', 'category': 'success'}, 200
        else:
            return {'message': msg.get('message'), 'category': 'error'}, 400

    except Exception as e:
        print(f'Error in importing deck deck:{e}')
        return {'message': 'Backend error. Try again', 'category': 'error'}, 500
        


