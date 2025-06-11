from flask import Blueprint, render_template, request, session, redirect, url_for


#initializing the auth blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")

#login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")