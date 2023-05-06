from werkzeug.exceptions import HTTPException
from flask import make_response, jsonify
import json


# --------------------  General Error Classes  --------------------
class Success_200(HTTPException): # 200
    def __init__(self, status_code=200, status_msg='Successful Request', category='success'):
        message = { 'message':status_msg,
                    'category':category,
                    'status':status_code }
        self.response = make_response(jsonify(message), status_code)


class Success_201(HTTPException): # 201
    def __init__(self, status_code=201, status_msg='Successful Request', category='success'):
        message = { 'message':status_msg,
                    'category':category,
                    'status':status_code }
        self.response = make_response(jsonify(message), status_code)


class InvalidDataError(HTTPException): # 400
    def __init__(self, status_code=400, status_msg='Invalid Data Error', category='error'):
        message = { 'message':status_msg,
                    'category':category,
                    'status':status_code }
        self.response = make_response(jsonify(message), status_code)


class NotFoundError(HTTPException): # 404
    def __init__(self, status_code=404, status_msg='Data Not Found Error', category='error'):
        message = {'message': status_msg,
                   'category': category,
                   'status': status_code}
        self.response = make_response(jsonify(message), status_code)


class AlreadyExistError(HTTPException): # 409
    def __init__(self, status_code=409, status_msg='Data Already Exist Error', category='error'):
        message = {'message': status_msg,
                   'category': category,
                   'status': status_code}
        self.response = make_response(jsonify(message), status_code)


class InternalServerError(HTTPException): # 500
    def __init__(self, status_code=500, status_msg='Internal Server Error', category='error'):
        message = { 'message':status_msg,
                    'category':category,
                    'status':status_code }
        self.response = make_response(jsonify(message), status_code)
