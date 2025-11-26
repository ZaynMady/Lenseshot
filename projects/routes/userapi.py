from flask import Blueprint, request, jsonify

#loading enviornmental variables and requests
import os
from dotenv import load_dotenv
load_dotenv()
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
#initializing authentication utility
from utilities.auth import supabase_jwt_required, get_current_user_id
#initializing database and Storage classes
from models.projectDb import ProjectDb
from utilities.cloudflareStorage import Cloudflare
DATABASE_URL = os.getenv("DATABASE_URL")
CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")      
SCREENPLAY_API_URL = os.getenv("SCREENPLAY_API_URL")
#intializing utility classes
import requests
db = ProjectDb(DATABASE_URL)
storage = Cloudflare(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY, CLOUDFLARE_BUCKET_NAME)

#initializing a project handler class
from common.Project import Project
project_handler = Project(storage, db)

#declaring a blueprint
userapi_bp = Blueprint('userapi', __name__, url_prefix='/api')

@userapi_bp.route('/projects/create', methods=['POST', 'OPTIONS'])
@supabase_jwt_required
def create_project():
    if request.method == 'OPTIONS':
        return "", 200
    
    #getting response from fontend
    response = request.json

    #extracting relevant data from the response
    project_metadata = response.get('metadata', {})
    
    if not project_metadata:
        return jsonify({"message": "Metadata is required"}), 400
    
    #extracting the metadata
    project_title = project_metadata.get('title')
    if not project_title:
        return jsonify({"message": "Project title is required in metadata"}), 400
    
    #getting the current user
    current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

    #uploading the metadata to cloud storage
    try:
        project_id = project_handler.create(current_user, project_title, project_metadata)
        return jsonify({"message": "Project created successfully", "project_id": project_id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"message": f"Failed to create project: {str(e)}"}), 500

@userapi_bp.route(f'/projects/<uuid:projectid>/metadata', methods=['OPTIONS', 'GET'])
@supabase_jwt_required
def metadata_project(projectid):
    if request.method == 'OPTIONS':
        return "", 200

    if request.method == 'GET':
    #getting the user id from the token
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        try:
            data = project_handler.get_metadata(current_user, projectid)
            return jsonify(data), 200
        
        except Exception as e:
            db.rollback()
            return jsonify({"message": f"Failed to retrieve metadata: {str(e)}"}), 500
        
@userapi_bp.route(f'/projects/<uuid:projectid>', methods=['DELETE', 'OPTIONS'])
@supabase_jwt_required
def delete_project(projectid):
    if request.method == 'OPTIONS':
        return "", 200
    if request.method == 'DELETE':
        #getting the user id from the token 
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        try:
            #sending a request to delete any screenplay data from the screenplay microservice
            screenplay_delete_url = f"{SCREENPLAY_API_URL}/projectAPI/screenplay/delete_project"
            payload = {
                "user_id": current_user,
                "project_id": str(projectid)
            }
            screenplay_response = requests.post(screenplay_delete_url, json=payload)
            
            # Check if the request to the screenplay service was successful, handle if not
            if screenplay_response.status_code not in [200, 404]: #404 is ok if no scripts existed
                return jsonify({"message": "Failed to delete associated screenplay data", "error": screenplay_response.json().get('msg')}), screenplay_response.status_code

            try:
                project_handler.delete_project(current_user, projectid)
                return jsonify({"message": "Project deleted successfully"}), 200
            except Exception as e:
                db.rollback()
                return jsonify({"message": f"Failed to delete project: {str(e)}"}), 500
        except Exception as e:
            db.rollback()
            return jsonify({"message": f"Failed to delete project: {str(e)}"}), 500


@userapi_bp.route(f'/projects/<uuid:projectid>/metadata', methods=['OPTIONS', 'PUT'])
@supabase_jwt_required
def update_metadata(projectid):
    if request.method == 'OPTIONS':
        return "", 200

    if request.method == 'PUT':
        #getting the user id from the token 

        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        new_metadata = request.json.get('metadata', {})
        if not new_metadata:
            return jsonify({"message": "Metadata is required"}), 400


        try:
            #downloading the existing metadata from the storage bucket
            project_handler.update_metadata(current_user, projectid, new_metadata)
            return jsonify({"message": "Metadata updated successfully"}), 200

        except Exception as e:
            db.rollback()
            return jsonify({"message": f"Failed to update metadata: {str(e)}"}), 500

@userapi_bp.route('/projects/list', methods=['GET', 'OPTIONS'])
@supabase_jwt_required
def list_projects():
    if request.method == 'OPTIONS':
        return "", 200

    if request.method == 'GET':
        #getting the user id from the token
        current_user = get_current_user_id(request, SUPABASE_JWT_SECRET)[0]

        try:
            projects = project_handler.list_projects(current_user)
            metadata_list = []
            for proj in projects:
                project_id = proj.id
                try:
                    metadata = project_handler.get_metadata(current_user, project_id)
                    #adding project_id to metadata
                    metadata['project_id'] = str(project_id)
                    metadata_list.append(metadata)
                except Exception as e:  
                    db.rollback()
                    return jsonify({"msg": "issue with storage cloudflare", "error" : str(e)}), 500
                   
            return jsonify(metadata_list), 201           
                
        except Exception as e:
            db.rollback()
            return jsonify({"message": f"Failed to retrieve projects: {str(e)}"}), 500
