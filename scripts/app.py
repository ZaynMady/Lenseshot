from flask import Flask
from flask_cors import CORS
import sentry_sdk


def create_app():

    app = Flask(__name__)


    sentry_sdk.init(
        dsn="https://fa944fec2f507e6ea4b2c61dbe9c900c@o4510484098580480.ingest.de.sentry.io/4510484186595408",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )
   
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})


    #loading blueprints
    from routes.userapi import userapi_bp
    from routes.projects import projects_bp
    app.register_blueprint(userapi_bp) #blueprint that interacts with the frontend
    app.register_blueprint(projects_bp) #blueprint that manages project related tasks

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000 , debug=True)