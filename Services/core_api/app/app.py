from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app(__name__):

    #initializing the app, database and login manager
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Creates database file in instance folder
    db.init_app(app)

    login_manager.init_app(app)


    #accessing routes


    return app
