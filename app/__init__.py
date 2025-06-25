from flask import Flask 
from .models import db
from .routes.auth import bcrypt, jwt
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import redirect, url_for, render_template





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
 

    #registering blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp) #User Authentication routes
    app.register_blueprint(dashboard_bp) #Dashboard routes



    #creating a base route for the application 
    @app.route('/')
    def index():
        verify_jwt_in_request(optional=True)  # Check if JWT is present, but not required
        user_id = get_jwt_identity()

        if user_id:
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            return redirect(url_for('auth_bp.login'))
        
    #returning the app instance
    return app