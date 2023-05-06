import os, json, time, requests, jwt
from datetime import datetime, timedelta
from functools import wraps
import random

from .models import Users
from .database import db
from .api import token_required

from flask import render_template, request, redirect, flash, url_for
from flask import current_app as app

#from application import tasks
#from application.workers import add

from .redis_cache import myRedis

    
BASE = 'http://127.0.0.1:5000' #'http://0.0.0.0:8080'

db.create_all()
db.session.commit()

root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def deleter():
    path_to_file = os.path.join(root, 'application\__pycache__', 'workers.cpython-37.pyc') #workers cpython file
    if os.path.exists(path_to_file):
        os.remove(path_to_file)


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
def home():
    return render_template('home.html')


# ---------------------- Extra Feature: Import & Export deck ------------------------


@app.route('/job_status', methods=['GET'])
@token_required
def check_job_status():
    print('Checking job status')
    _id = request.headers.get('job_id')
    print(f"\n\nJob id: {_id}\n\n")
    print(f"\n\ncelery-task-meta-{_id}\n\n")
    print(f"\n\nJob id: {myRedis.get(f'celery-task-meta-{_id}')}\n\n")
    status = json.loads(myRedis.get(f'celery-task-meta-{_id}').decode("utf-8"))
    if status['status'] == 'SUCCESS':
        return status['result'][0], status['result'][1]
    else:
        return {'message': 'Task failed', 'category': 'error'}, 500



@app.route('/generate_report', methods=['GET'])
@token_required
def generate_report():
    from .workers import report_generate_async
    token = myRedis.get('token').decode("utf-8")
    current_user = json.loads(myRedis.get('current_user'))
    job = report_generate_async.apply_async([token, current_user])
    time.sleep(1)
    #result = job.wait()
    deleter()
    print(f'job id:{job.id}')
    return {'message': 'Report generate task in progress', 'category': 'success', 'job_id':job.id}, 200
    
    
@app.route('/deck/<int:deckid>/export', methods=['GET', 'POST'])
@token_required
def exportDeck(deckid):
    from .workers import export_deck_async
    token = myRedis.get('token').decode("utf-8")
    current_user = json.loads(myRedis.get('current_user'))
    job = export_deck_async.apply_async([deckid, token, current_user])
    time.sleep(1)
    #result = job.wait()
    deleter()
    print(f'job id:{job.id}')
    return {'message': 'Export task in progress', 'category': 'success', 'job_id':job.id}, 200
    
    


@app.route('/deck/import', methods=['POST'])
def importDeck():
    from .workers import import_deck_async
    token = myRedis.get('token').decode("utf-8")
   
    try:
        deckname = request.form.get('deckname')
        deckdesc = request.form.get('deckdesc')
        deckfile = request.files['file']
        deckfile.save(os.path.join(root,'Imports',deckfile.filename))
    except Exception as e:
        print(f'Error in import deck:{e}')
        return {'category': 'error', 'message': 'Error at backend'}, 500
    else:
        job = import_deck_async.apply_async([deckfile.filename, deckname, deckdesc, token])
        result = job.wait()
        deleter()
        return result[0], result[1]
        
        
@app.route('/send_alert', methods=['GET'])
def send_alert():
    from .workers import send_alert_async
    all_users = json.loads(myRedis.get('all_users').decode("utf-8"))
    job = send_alert_async.apply_async([all_users])
    deleter()
    return {'message': 'ALert sent', 'category': 'success', 'job_id':job.id}, 200
    

    

