import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    #SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"


class LocalDevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///databases/flashCardDB.sqlite3?charset=utf8'
    SECRET_KEY = 'secretKey'
    DEBUG = True
    
    #SECURITY_FRESHNESS_GRACE_PERIOD = timedelta(hours=1)
    # SECURITY_PASSWORD_HASH = "bcrypt"
    # SECURITY_PASSWORD_SALT = "really super secret"
    # SECURITY_REGISTERABLE = True
    # SECURITY_CONFIRMABLE = False
    # SECURITY_SEND_REGISTER_EMAIL = False
    # SECURITY_UNAUTHORIZED_VIEW = None
    # WTF_CSRF_ENABLED = False
