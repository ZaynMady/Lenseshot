from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_login import UserMixin
from . import db




class user(db.Model, UserMixin):
    #here is the information that is needed from the user, this is going to be aside from their profile bio which will be added when collab is added
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    #this function registers the user if not already in our database
    def register_user():
        ...

    #this authenticates the user 
    def authenticate_user():
        ...