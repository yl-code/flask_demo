import os
from sayhello import app

SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/sayhello'
