from flask import Flask 
from .models import db
from .routes.auth import bcrypt, login_manager





#Create App Function 

def create_app():
    
    app = Flask(__name__)

    #intializing application instances
    bcrypt.init_app(app)
    login_manager.init_app(app)

    #loading configuration
    from .config import config
    app.config.from_object(config)

    #app database
    db.init_app(app)
    

    #registering blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)


    #returning the app instance
    return app



