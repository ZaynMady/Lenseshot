from flask import Blueprint,  redirect, url_for, make_response, request, jsonify
from app.models.userbase import user
from app.models import db
from flask_bcrypt import Bcrypt 
from flask import flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, unset_jwt_cookies
import os

#initializing the auth blueprint
auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")
bcrypt = Bcrypt()

#initializing the login manager
jwt = JWTManager()


#login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        #get the data
        data = request.get_json()

        #parse the data
        email = data.get("email")
        password = data.get("password")

        #validating the data
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        
        #checking if the user exists
        User = user.query.filter_by(email=email).first()
        if not User:
            return jsonify({"message": "User not found"}), 404
        #checking if the password is correct
        if not bcrypt.check_password_hash(User.password, password):
            return jsonify({"message": "Invalid password"}), 401
        #creating a JWT token for the user
        access_token = create_access_token(identity=str(User.id))
        
        return jsonify({ "message": "login successfull", "access_token": access_token, "success": True}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

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
    try:
        data = request.get_json() 
        if not data:
            return jsonify({"message": "No data provided"}), 400
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        User = user(
            username=username,
            email=email,
            password=bcrypt.generate_password_hash(password).decode('utf-8')
        )
        db.session.add(User)
        db.session.commit()

        #creating a user folder
        user_folder = os.path.join("users", str(User.id))
        os.makedirs(user_folder, exist_ok=True)
        #if the user folder could not be created, return an error
        if not user_folder:
            return jsonify({"message": "User folder could not be created"}), 500
        return jsonify({"message": "User registered successfully", "success": True}), 201
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500