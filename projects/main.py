from flask import Flask 
from flask_cors import CORS
from flask import jsonify, request
import requests

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"   # 👈 REQUIRED
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]      # default, but be explicit
    app.config["JWT_HEADER_TYPE"] = "Bearer"            # so it matches "Authorization: Bearer <token>"
    #Enable CORS for the app
    CORS(app, 
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:5173", 
                                        "http://localhost:5000"]}}) #Enable CORS for the app

    # This should point to your backend service in docker-compose
    BACKEND_URL = "http://backend:5000/api"

    #Basic CRUD

    @app.route(f'/api/projects/create', methods=['POST', 'OPTIONS'])
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
        
        #generating headers
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Authorization header is missing"}), 401

        headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = auth_header

        payload = {
            'metadata': project_metadata,
            'project_title': project_title
        }

        #send a post request to the backend to create a new project
        backend_response = requests.post(f'{BACKEND_URL}/create_project', json=payload, headers=headers)
        if backend_response.status_code == 201:
            return jsonify(backend_response.json()), 201
        else:
            return jsonify({"message": "Failed to create project", "details": backend_response.text}), backend_response.status_code

    @app.route(f'/api/projects/<int:projectid>/metadata', methods=['OPTIONS', 'GET'])
    def metadata_project(projectid):
        if request.method == 'OPTIONS':
            return "", 200

        if request.method == 'GET':
            #generating headers
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Authorization header is missing"}), 401
            headers = {'Content-Type': 'application/json'}
            headers['Authorization'] = auth_header

            body = {
                'project_id': projectid
            }

            #send a get request to the backend to fetch project details
            backend_response = requests.post(f'{BACKEND_URL}/project_details/{int(projectid)}', headers=headers, json=body)
            if backend_response.status_code == 200:
                return jsonify(backend_response.json()), 200
            else:
                return jsonify({"message": "Failed to fetch project details", "details": backend_response.text}), backend_response.status_code
    @app.route(f'/api/projects/<int:projectid>', methods=['DELETE'])
    def delete_project(projectid):
        #generating headers
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Authorization header is missing"}), 401
        headers = {'Content-Type': 'application/json'}
        headers['Authorization'] = auth_header

        #send a delete request to the backend to delete the project
        backend_response = requests.delete(f'{BACKEND_URL}/delete_project/{int(projectid)}', headers=headers)
        if backend_response.status_code == 200:
            return jsonify(backend_response.json()), 200
        else:
            return jsonify({"message": "Failed to delete project", "details": backend_response.text}), backend_response.status_code

    @app.route(f'/api/projects/<int:projectid>/metadata', methods=['OPTIONS', 'PUT'])
    def update_metadata(projectid):
        if request.method == 'OPTIONS':
            return "", 200

        if request.method == 'PUT':
            #generating headers
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Authorization header is missing"}), 401
            headers = {'Content-Type': 'application/json'}
            headers['Authorization'] = auth_header

            response = request.json
            project_metadata = response.get('metadata', {})
            
            if not project_metadata:
                return jsonify({"message": "Metadata is required"}), 400

            body = {
                'metadata': project_metadata
            }

            #send a put request to the backend to update project metadata
            backend_response = requests.put(f'{BACKEND_URL}/update_project/{int(projectid)}', headers=headers, json=body)
            if backend_response.status_code == 200:
                return jsonify(backend_response.json()), 200
            else:
                return jsonify({"message": "Failed to update project metadata", "details": backend_response.text}), backend_response.status_code
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=7000)