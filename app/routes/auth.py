from flask import Blueprint, render_template, request, session, redirect, url_for
from app.forms import registrationForm, loginForm

#initializing the auth blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")

#login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()
    return render_template("login.html", title="Login", form=form)

#register route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = registrationForm()
    return render_template("register.html", title="Register", form=form)