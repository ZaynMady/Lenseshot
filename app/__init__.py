from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


#Setting up Database Variable
db = SQLAlchemy()

#Create App Function 

def create_app():
    
    app = Flask(__name__)

    #loading configuration
    from .config import config
    app.config.from_object(config)

    #app database
    db.init_app(app)

    return app





