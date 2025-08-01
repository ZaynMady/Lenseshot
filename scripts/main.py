from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

app = Flask(__name__)

# This should point to your backend service in docker-compose
BACKEND_URL = "http://localhost:5000/api/"

@app.route('/api/create_screenplay', methods=['POST'])
@jwt_required()
def create_screenplay():
    URL = BACKEND_URL + 'screenplays/create'
    data = request.json

    template_name = data.get('template_name')
    screenplay_name = data.get('screenplay_name')
    project_id = data.get('project_id')
    current_user = get_jwt_identity()

    if not all([template_name, screenplay_name, project_id]):
        return jsonify({'msg': 'Missing required fields'}), 400

    # Load the template
    template_path = os.path.join('templates', template_name)
    if not os.path.exists(template_path):
        return jsonify({'msg': 'Template not found'}), 404

    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template_content = template_file.read()
    except Exception as e:
        return jsonify({'msg': 'Error reading template', 'error': str(e)}), 500

    # Forward the screenplay content to backend microservice
    payload = {
        'screenplay_name': screenplay_name,
        'project_id': project_id,
        'user_id': current_user,
        'content': template_content
    }

    try:
        response = request.post(URL, json=payload)
    except request.exceptions.RequestException as e:
        return jsonify({'msg': 'Failed to communicate with backend service', 'error': str(e)}), 502

    if response.status_code != 201:
        return jsonify({'msg': 'Backend failed to save screenplay', 'details': response.text}), response.status_code

    return jsonify({'msg': 'Screenplay created successfully'}), 201

