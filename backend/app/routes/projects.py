from flask import Blueprint, jsonify, request, json
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

#Define a route to handle project-related requests
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    ...

def create_project():
    current_user = get_jwt_identity()
    meta_data = request.json.get('metadata', {})
    #if there is no metadata, return an error
    if not meta_data:
        return jsonify({"message": "Metadata is required"}), 400
    
    project_name = request.json.get('name')

    project_path = os.path.join('users', str(current_user), 'projects', project_name)
    #if project does not exist, create it 
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    #if project already exists
    if os.path.exists(project_path):
        return jsonify({"message": "Project already exists"}), 400
    
    file_path = os.path.join(project_path, 'metadata.json')
    #write metadata to file
    with open(file_path, 'w') as f:
        json.dump(meta_data, f)
    return jsonify({"message": "Project created successfully"}), 201


def delete_project(project_id):
    ...

