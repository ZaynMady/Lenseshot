#creating a flask blueprint for project related routes
from flask import Blueprint, request, jsonify

projects_bp = Blueprint('projects', __name__, url_prefix='/projectAPI')

#initializing database and Storage classes
from models.ScriptDB import ScriptDB
from utilities.cloudflareStorage import Cloudflare
import os

#loading environmental variables
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")

#intializing utility classes
db = ScriptDB(DATABASE_URL)
storage = Cloudflare(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY, CLOUDFLARE_BUCKET_NAME)

#initializing a script handler class
from common.Script import Script
script = Script(storage, db)

#route to delete a project and all associated scripts
@projects_bp.route('screenplay/delete_project', methods=['POST', 'OPTIONS'])
def delete_project():
    if request.method == "OPTIONS":
        return "", 200
    
    #getting the required data [user_id and project_id]
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    if not all([user_id, project_id]):
        return jsonify({'msg': 'Missing required fields', "response": request.json}), 400
    
    #deleting all scripts associated with the project under the user id from both database and storage
    try:
        script.delete_project(user_id, project_id)
        return jsonify({'msg': "Project's associated scripts deleted successfully."}), 200
    except FileNotFoundError as fnf_error:
        db.rollback()
        return jsonify({'msg': str(fnf_error)}), 404
    except Exception as e:
        db.rollback()
        return jsonify({'msg': 'An error occurred while deleting the project.', 'error': str(e)}), 500