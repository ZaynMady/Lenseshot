from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_login import UserMixin
from . import db



# this class defines the user model for the application, which is used to store user information in the database.
class user(db.Model, UserMixin):

    __tablename__ = 'users'  # Define the table name for the user model
    
    #important sign in infromation, these cannot be skipped
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    username = db.Column(db.String(200),unique=True, nullable=False)
    email = db.Column(db.String(200),unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    #additional information 
    role = db.Column(db.String(50), nullable=True)
    rate = db.Column(db.Float, default=0.0, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True, default='static/img/profile_picture.jpg')
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)