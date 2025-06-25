from flask import Blueprint, render_template, redirect, url_for, jsonify, make_response
from app.forms import registrationForm, loginForm
from app.models.userbase import user
from app.models import db
from flask_bcrypt import Bcrypt 
from flask import flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies


#initializing the auth blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")
bcrypt = Bcrypt()

#initializing the login manager
jwt = JWTManager()


#login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = loginForm()

    User = user.query.filter_by(email=form.email.data).first()
    #if User Submits the form and it is valid
    if form.validate_on_submit():
        #checking if the user exists
        if User and bcrypt.check_password_hash(User.password, form.password.data):
            #if the user exists and the password is correct
            access_token = create_access_token(identity=str(User.id)) #creating a JWT token for the user
            response = make_response(redirect(url_for("dashboard_bp.dashboard")))
            set_access_cookies(response, access_token) #redirecting to the dashboard page
            return response 
        else:
            #if the user does not exist or the password is incorrect
            form.email.errors.append("Invalid email or password")
            flash("Invalid email or password", "danger")

    return render_template("login.html", title="Login", form=form)

#logout route
@auth_bp.route("/logout")
@jwt_required()
def logout():
    #logout the user by removing the JWT token from the response cookie
    response = make_response(redirect(url_for("auth_bp.login")))
    unset_jwt_cookies(response)
    flash("You have been logged out successfully", "success")
    return response

#register route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = registrationForm()

    #if User Submits the form and it is valid
    if form.validate_on_submit():
        
        #hashing the password
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        #creating an instance of the user model with all the information 
        User = user(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(User)
        db.session.commit() 
        return redirect(url_for("auth_bp.login"))
    
    return render_template("register.html", title="Register", form=form)