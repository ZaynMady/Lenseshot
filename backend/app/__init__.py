from flask import Flask 
from app.models import db
from app.routes.auth import bcrypt, jwt
from flask import redirect, url_for, render_template
from flask_cors import CORS




#Create App Function 

def create_app():
    
    app = Flask(__name__)


    #Loading the configuration from the config file
    from .config import config
    app.config.from_object(config)   

    #intializing application instances
    bcrypt.init_app(app) #Password hashing
    jwt.init_app(app) #JWT Authentication
    db.init_app(app) #Database connection
    CORS(app, 
    supports_credentials=True,
    origins=["http://localhost:5173"] ) #Enable CORS for the app
 

    #registering blueprints
    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.user_account import user_account_bp

    app.register_blueprint(auth_bp, url_prefix="/api") #User Authentication routes
    app.register_blueprint(projects_bp, url_prefix="/api") #Dashboard routes
    app.register_blueprint(user_account_bp, url_prefix="/api") #User Account routes



    #handling different jwt errors

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auth_bp.login', message="Your session has expired. Please log in again."))
    
    @jwt.invalid_token_loader
    def invalid_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auth_bp.login', message="Invalid token. Please log in again."))
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_message):
        return redirect(url_for('auth_bp.login', message=error_message))
    
    
        
    #returning the app instance
    return app