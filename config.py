# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Loginto12@localhost/control'
    SQLALCHEMY_TRACK_MODIFICATIONS = False