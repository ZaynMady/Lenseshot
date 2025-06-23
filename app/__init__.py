from flask import Flask 
from .models import db
from .routes.auth import bcrypt, login_manager





#Create App Function 

def create_app():
    
    app = Flask(__name__)

    #Loading the configuration from the config file
    from .config import config
    app.config.from_object(config)   

    #intializing application instances
    bcrypt.init_app(app) #Password hashing
    login_manager.init_app(app) #Login manager for user sessions
    db.init_app(app) #Database connection
 

    #registering blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp) #User Authentication routes
    app.register_blueprint(dashboard_bp) #Dashboard routes


    #returning the app instance
    return app