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

    project_name = request.json.get('project_title')
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

@projects_bp.route('/project_details/<int:project_id>', methods=['GET', 'POST'])
@jwt_required()
def get_project_details(project_id):
    current_user = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, owner=current_user).first()

    if not project:
        return jsonify({"message": "Project not found"}), 404

    project_path = os.path.join('users', str(current_user), 'projects', str(project_id))
    metadata_file = os.path.join(project_path, 'metadata.json')

    if not os.path.exists(metadata_file):
        return jsonify({"message": "Metadata file not found"}), 404

    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            return jsonify(metadata), 200
    except Exception as e:
        print(f"Failed to read metadata for project {project.id}: {e}")
        return jsonify({"message": "Failed to read metadata"}), 500

@projects_bp.route('/update_project/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, owner=current_user).first()

    if not project:
        return jsonify({"message": "Project not found"}), 404

    metadata = request.json.get('metadata', {})
    if not metadata:
        return jsonify({"message": "Metadata is required"}), 400

    project_path = os.path.join('users', str(current_user), 'projects', str(project_id))
    metadata_file = os.path.join(project_path, 'metadata.json')

    if not os.path.exists(metadata_file):
        return jsonify({"message": "Metadata file not found"}), 404

    try:
        with open(metadata_file, 'r') as f:
            existing_metadata = json.load(f)
            existing_metadata.update(metadata)

        with open(metadata_file, 'w') as f:
            json.dump(existing_metadata, f)

        return jsonify({"message": "Project updated successfully"}), 200
    except Exception as e:
        print(f"Failed to update metadata for project {project.id}: {e}")
        return jsonify({"message": "Failed to update metadata"}), 500

@projects_bp.route('/delete_project/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):

    if not project_id:
        return jsonify({"message": "Project ID is required"}), 400

    current_user = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, owner=current_user).first()

    if not project:
        return jsonify({"message": "Project not found"}), 404

    # Delete project from database
    db.session.delete(project)
    db.session.commit()

    # Delete project directory
    project_path = os.path.join('users', str(current_user), 'projects', str(project_id))
    if os.path.exists(project_path):
        try:
            import shutil
            shutil.rmtree(project_path)
        except Exception as e:
            print(f"Error deleting project files: {e}")
            return jsonify({"message": "Project deleted from database but failed to delete files"}), 500

    return jsonify({"message": "Project deleted successfully"}), 200

