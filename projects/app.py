from flask import Flask 
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)

    #Enable CORS for the app
    CORS(app, 
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:5173", 
                                        "http://localhost:5000"]}}) #Enable CORS for the app

    #setting up blueprints
    from routes.userapi import userapi_bp
    app.register_blueprint(userapi_bp)


    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=7000, debug=True)