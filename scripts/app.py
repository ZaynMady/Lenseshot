from flask import Flask
from flask_cors import CORS


def create_app():

    app = Flask(__name__)
   
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})


    #loading blueprints
    from scripts.routes.userapi import userapi_bp
    from scripts.routes.projects import projects_bp
    app.register_blueprint(userapi_bp) #blueprint that interacts with the frontend
    app.register_blueprint(projects_bp) #blueprint that manages project related tasks

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000 , debug=True)