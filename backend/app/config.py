import os

class config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'mysql+pymysql://root:earth616@db:3306/lenseshot')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"
    JWT_COOKIE_SECURE = False  # True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT = False
