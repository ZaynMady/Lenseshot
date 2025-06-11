from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, length, Email, EqualTo


# This file contains the forms used for user registration and login in a Flask application.
# It uses Flask-WTF for form handling and validation.
class registrationForm(FlaskForm):
    username = StringField("Username", 
                           render_kw={"placeholder": "Enter your username"}, 
                           validators=[DataRequired(), 
                                       length(min=2, max=20)])
    
    email = EmailField("Email",
                       render_kw={"placeholder": "Enter your email"}, 
                       validators=[DataRequired(), 
                                   Email()])
    
    password = PasswordField("Password",
                            render_kw={"placeholder": "Enter your password"}, 
                            validators=[DataRequired(), 
                                        length(min=6, max=20)])
    
    confirm_password = PasswordField("Confirm Password",
                                    render_kw={"placeholder": "Confirm your password"}, 
                                    validators=[DataRequired(), 
                                                EqualTo("password", 
                                                        message="Passwords must match")])
    
    submit = SubmitField("Submit")

class loginForm(FlaskForm):

    email = EmailField("Email",
                       render_kw={"placeholder": "Enter your email"}, 
                       validators=[DataRequired(), 
                                   Email()])
    
    password = PasswordField("Password",
                            render_kw={"placeholder": "Enter your password"}, 
                            validators=[DataRequired(), 
                                        length(min=6, max=20)])
    
    remember = BooleanField("Remember Me")
    
    submit = SubmitField("Login")