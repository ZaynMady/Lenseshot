from flask import Flask
from flask_cors import CORS

def create_app():

    app = Flask(__name__)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    #loading blueprints


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=2000 , debug=True)