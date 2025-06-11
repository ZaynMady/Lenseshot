import os

class config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'mysql+pymysql://root:earth616@localhost:3306/lenseshot')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
