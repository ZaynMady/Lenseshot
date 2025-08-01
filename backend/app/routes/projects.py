from flask import Blueprint, jsonify, request, json
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from app.models import db
from app.models.projects import Project

#Define a route to handle project-related requests
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def fetch_projects():
    #getting all projects owned by the user
    current_user = get_jwt_identity()
    projects = Project.query.filter_by(owner=current_user).all()

    #initalizing a metadata list to store all project metadata
    all_metadata = []

    #iterating through each project to fetch its metadata
    for project in projects:
        project_path = os.path.join('users', str(current_user), 'projects', str(project.id))
        metadata_file = os.path.join(project_path, 'metadata.json')

        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    metadata['project_id'] = project.id  # Include ID so frontend can build links
                    all_metadata.append(metadata)
            except Exception as e:
                # Log the error, skip corrupted or unreadable files
                print(f"Failed to read metadata for project {project.id}: {e}")
                continue

    return jsonify(all_metadata), 200


@projects_bp.route('/create_project', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    meta_data = request.json.get('metadata', {})

    if not meta_data:
        return jsonify({"message": "Metadata is required"}), 400

    project_name = meta_data.get('name')
    if not project_name:
        return jsonify({"message": "Project name is required in metadata"}), 400

    # Check if user already has a project with this name
    existing = Project.query.filter_by(owner=current_user, name=project_name).first()
    if existing:
        return jsonify({"message": "Project with this name already exists"}), 400

    # Save project to database
    project = Project(owner=current_user, name=project_name)
    db.session.add(project)
    db.session.commit()

    project_id = project.id
    project_path = os.path.join('users', str(current_user), 'projects', str(project_id))

    os.makedirs(project_path, exist_ok=True)

    # Save metadata to metadata.json
    file_path = os.path.join(project_path, 'metadata.json')
    with open(file_path, 'w') as f:
        json.dump(meta_data, f)

    return jsonify({"message": "Project created successfully", "project_id": project_id}), 201


def delete_project(project_id):
    ...

