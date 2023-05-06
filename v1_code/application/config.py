import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None

class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databases/flashCardDB.sqlite3?charset=utf8'
    SECRET_KEY = 'secretKey'
    DEBUG = True
