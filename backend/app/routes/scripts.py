from flask import Blueprint, jsonify, request, json, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from app.models import db

# Define a blueprint for script-related routes
scripts_bp = Blueprint("screenplay", __name__)



#route to create a new screenplay from a template
@scripts_bp.route('screenplay/create', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_screenplay():
    data = request.json

    content = data.get('content')       # e.g., "american_screenplay.xml"
    screenplay_name = data.get('screenplay_name')   # e.g., "MyFirstScript"
    project_id = data.get('project_id')             # e.g., "123"
    current_user = get_jwt_identity()               # comes from JWT  
    
    #create the path to create the screenplay
    if not all([screenplay_name, project_id, content]):
        return jsonify({'msg': 'Missing required fields', "response": request.json }), 400
    
    path = os.path.join('users', str(current_user), 'projects', str(project_id))
    if not os.path.exists(path):
        return jsonify({'msg': 'Project not found'}), 404
    
    screenplay_path = os.path.join(path, "scripts", f"{screenplay_name}.xml")


    if os.path.exists(screenplay_path):
        return jsonify({'msg': 'Screenplay already exists'}), 400
    
        #creating the file
    os.makedirs(os.path.dirname(screenplay_path), exist_ok=True)

    with open(screenplay_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return jsonify({'msg': 'Screenplay created successfully', 'path': screenplay_path}), 201
"""
@scripts_bp.route('/list', methods=['POST'])
@jwt_required
def list_screenplays():
    data = request.json

    #extracting the necessary fields
    user_id = data.get("user_id")
    project_id = data.get("project_id")

    #querying the project path looking for all screenplays in that project

    if not all([user_id, project_id]):
        return jsonify({'msg': 'Missing required fields'}), 400
    
    project_path = os.path.join('users', str(user_id), 'projects', str(project_id))
    if not os.path.exists(project_path):
        return jsonify({'msg': 'Project not found'}), 404
    screenplays = [f for f in os.listdir(project_path) if f.endswith('.xml')]
    return jsonify({'screenplays': screenplays}), 200


# route to open an existing screenplay
@scripts_bp.route('open', methods=['POST'])
@jwt_required()
def open_screenplay():
    #getting metadata from request
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    screenplay_name = data.get('screenplay_name')

    if not all([user_id, project_id, screenplay_name]):
        return jsonify({'msg': 'Missing required fields'}), 400
    
    #querying the backend microservice to get the screenplay file

    screenplay = os.path.join('users', str(user_id), 'projects', str(project_id), f"{screenplay_name}.xml")

    if not screenplay: 
        return jsonify({'msg': 'Screenplay not found'}), 404
    try: 
        with open(screenplay, 'r') as f:
            content = f.read()
        return jsonify({'content': content}), 200
    except Exception as e:
        return jsonify({'msg': 'Error reading screenplay', 'error': str(e)}), 500
    
"""