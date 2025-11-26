#this file exposes screenplay data to the frontend
from flask import Blueprint, request, jsonify
from utilities.auth import supabase_jwt_required, get_current_user_id
from xml.etree import  ElementTree as ET

userapi_bp = Blueprint('userapi_bp', __name__, url_prefix='/api')

#loading environemntal variables
import os
from dotenv import load_dotenv
import uuid

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

#initializing database and Storage classes
from models.ScriptDB import ScriptDB
from utilities.cloudflareStorage import Cloudflare

db = ScriptDB(DATABASE_URL)
Storage = Cloudflare(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY, CLOUDFLARE_BUCKET_NAME)

#initializing a script handler class
from common.Script import Script

#route to create a screenplay
@userapi_bp.route('/create_screenplay', methods=['POST', 'OPTIONS', "GET"])
@supabase_jwt_required
def create_screenplay():
    #Handling an Options request 
    if request.method == "OPTIONS":
        return "", 200 
    
    #extracting the request body and headers
    data = request.json

    #getting current user's id
    try:
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]
    except Exception as e:
        db.rollback()
        return jsonify({"msg": "Unauthorized", "error": str(e)}), 401
    
    #extracting important information necessary to create a screenplay
    template_name = data.get('template_name')       
    screenplay_name = data.get('screenplay_name')   
    project_id = data.get('project_id')             

    if not all([template_name, screenplay_name, project_id]):
        return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

    #finding the path to the template LSS file
    template_path = os.path.join('templates', template_name)
    if not os.path.exists(template_path):
        return jsonify({'msg': 'Template not found'}), 404

    #parsing XML to String content
    try:
        # Parse XML template
        tree = ET.parse(template_path)
        root = tree.getroot()

        # Convert XML to string
        template_content = ET.tostring(root, encoding="unicode")
    except Exception as e:
        db.rollback()
        return jsonify({'msg': 'Error reading template', 'error': str(e)}), 500


    #saving it to storage
    try:
        #intializing a script and storing it in storage
        screenplay = Script(StorageClass=Storage, DatabaseClass=db)
        screenplay.create(content=template_content, title=screenplay_name, user=current_user, project=project_id)
        return jsonify({'msg': 'Screenplay created successfully'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'msg': 'storage connection failed', 'error': str(e)}), 502

#route to open a screenplay 
@userapi_bp.route("/open_screenplay", methods=['GET', 'POST', 'OPTIONS'])
@supabase_jwt_required
def open_screenplay():
    if request.method == "OPTIONS":
        return "", 200

    #getting requested data and headers
    data = request.json
    
    #getting current user's id
    try:
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]
    except Exception as e:
        db.rollback()
        return jsonify({"msg": "Unauthorized", "error": str(e)}), 401
    
    #getting screenplay data from request necessary to find the file
    screenplay_name = data.get('screenplay_name')   
    project_id_str = data.get('project_id')             

    if not all([screenplay_name, project_id_str]):
        return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

    try:
        # Remove the .lss extension from the incoming name to match the database title
        title_without_extension = screenplay_name.replace(".lss", "")

        project_id = uuid.UUID(project_id_str) # Convert string to UUID object
        screenplay = Script(StorageClass=Storage, DatabaseClass=db)
        screenplay.open(title=title_without_extension, user=current_user, project=project_id)
    except Exception as e:
        db.rollback()
        return jsonify({'msg': f'Backend connection failed: {str(e)}'}), 502

    if not screenplay.file_content:
        return jsonify({'msg': 'Screenplay content not found or failed to open'}), 404

    return jsonify({
        "style": screenplay.style,
        "smartTypes": screenplay.smarttypes,
        "content": screenplay.content,
        "components": screenplay.components
    })

#route to save a screenplay
@userapi_bp.route('/save_screenplay', methods=['POST', 'OPTIONS'])
@supabase_jwt_required
def save_screenplay():
        if request.method == "OPTIONS":
            return "", 200 
        data = request.json
        
        #getting current user's id
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        #getting important screenplay data
        screenplay_Json = data.get('screenplay')      
        screenplay_name = data.get('screenplay_name')
        project_id_str = data.get('project_id')
        if not all([screenplay_Json, screenplay_name, project_id_str]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        try: 
            title_without_extension = screenplay_name.replace(".lss", "")
            project_id = uuid.UUID(project_id_str)

            # Initialize the script object
            screenplay = Script(StorageClass=Storage, DatabaseClass=db)
            # Open the script to load its current state
            screenplay.open(title=title_without_extension, user=current_user, project=project_id)
            # Save the new content
            screenplay.save(title=title_without_extension, user=current_user, project=project_id, new_content=screenplay_Json)
        except Exception as e:
            db.rollback()
            return jsonify({'msg': 'Failed to save screenplay', 'error': str(e)}), 500

        return jsonify({"msg" : "Screenplay Saved Successfully"}), 200     

#route to delete a screenplay
@userapi_bp.route('/delete_screenplay', methods=['POST', 'OPTIONS'])
@supabase_jwt_required
def delete_screenplay():
        if request.method == "OPTIONS":
            return "", 200
        #getting data from frontend
        data = request.json 

        #extracting relevant information from data
        screenplay_name = data.get('screenplay_name')
        project_id_str = data.get('project_id')

        if not all ([screenplay_name, project_id_str]):
            return jsonify({'msg': "Missing required fields"}), 400

        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        #sending a request to the backend to delete the screenplay
        try: 
            title_without_extension = screenplay_name.replace(".lss", "")
            project_id = uuid.UUID(project_id_str)

            screenplay = Script(StorageClass=Storage, DatabaseClass=db)
            screenplay.delete(title=title_without_extension, user=current_user, project=project_id)
            return jsonify({"msg": "Screenplay Deleted Successfully"}), 200
        except Exception as e:
            db.rollback()
            return jsonify({'msg': f'Failed to delete screenplay: {str(e)}'}), 502
        
#route to get all screenplays under a project
@userapi_bp.route('/list_screenplays', methods=['POST', 'OPTIONS'])
@supabase_jwt_required
def list_screenplays():
    if request.method == "OPTIONS":
        return "", 200
    #getting data from frontend
    data = request.json
    project_id_str = data.get('project_id')
    if not project_id_str:
        return jsonify({'msg': "Missing required fields"}), 400
    #getting current user's id
    current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]
    try:
        project_id = uuid.UUID(project_id_str)
        # The method to list scripts is on the database object, not the Script object.
        screenplays_data = db.get_list_of_scripts(owner_id=current_user, project_id=project_id)
        screenplay_titles = [script.title for script in screenplays_data]
        return jsonify({"screenplays": screenplay_titles}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'msg': 'Failed to list screenplays', 'error': str(e)}), 502
    
