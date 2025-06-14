from flask import Blueprint, render_template, request, session, redirect, url_for
from app.forms import registrationForm, loginForm
from app.models.userbase import user
from app.models import db
from flask_bcrypt import Bcrypt 
from flask import flash
from flask_login import login_user, LoginManager, login_required, logout_user


#initializing the auth blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")
bcrypt = Bcrypt()

#initializing the login manager
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    # Load the user from the database using the user_id
    return user.query.get(int(user_id))


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
            login_user(User)  # Log the user in
            return redirect(url_for("dashboard_bp.dashboard"))
        else:
            #if the user does not exist or the password is incorrect
            form.email.errors.append("Invalid email or password")
            flash("Invalid email or password", "danger")

    return render_template("login.html", title="Login", form=form)

#logout route
@auth_bp.route("/logout")
@login_required 
def logout():
    logout_user()
    return redirect(url_for("auth_bp.login"))
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