from flask.app import Flask
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir,'.env'))


TESTING=True
DEBUG=True
FLASK_ENV='development'
SECRET_KEY=environ.get('SECRET_KEY')
#FLASK_APP=environ.get('APP_DIR')
#SERVER_NAME=environ.get('SERVER_URL')