from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import requests
from xml.etree import  ElementTree as ET
from flask_cors import CORS
from flask_jwt_extended import JWTManager




def create_app():


    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"   # 👈 REQUIRED
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]      # default, but be explicit
    app.config["JWT_HEADER_TYPE"] = "Bearer"            # so it matches "Authorization: Bearer <token>"
    JWTManager(app)
    #Enable CORS for the app
    CORS(app, 
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:5173", 
                                       "http://localhost:5000"]}}) #Enable CORS for the app
    
    # This should point to your backend service in docker-compose
    BACKEND_URL = "http://backend:5000/api"

    @app.route('/api/create_screenplay', methods=['POST', 'OPTIONS', "GET"])
    def create_screenplay():
        if request.method == "OPTIONS":
            return "", 200 
        data = request.json
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        headers = {"content-type": "application/json"}
        headers["Authorization"] = auth_header

        template_name = data.get('template_name')       # e.g., "american_screenplay.xml"
        screenplay_name = data.get('screenplay_name')   # e.g., "MyFirstScript"
        project_id = data.get('project_id')             # e.g., "123"               # comes from JWT

        if not all([template_name, screenplay_name, project_id]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        # Path to template XML file
        template_path = os.path.join('templates', template_name)
        if not os.path.exists(template_path):
            return jsonify({'msg': 'Template not found'}), 404

        try:
            # Parse XML template
            tree = ET.parse(template_path)
            root = tree.getroot()


            # Convert XML to string
            template_content = ET.tostring(root, encoding="unicode")
        except Exception as e:
            return jsonify({'msg': 'Error reading template', 'error': str(e)}), 500

        # Forward to backend microservice
        payload = {
            
            "screenplay_name": screenplay_name,
            "project_id": project_id,
            "content": template_content
        }

        try:
            response = requests.post(f"{BACKEND_URL}/screenplay/create", json=payload, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

        return jsonify(response.json()), response.status_code

    """
    @app.route('open_screenplay', methods=['GET'])
    @jwt_required()
    def open_screenplay():
        #Getting the script from the backend using the request response
        data = request.json 

        #extracting the necessary metadata
        user_id = data.get('user_id')
        project_id = data.get('project_id')
        screenplay_name = data.get('screenplay_name')

        if not all([user_id, project_id, screenplay_name]):
            return jsonify({'msg': 'Missing required fields'}), 400
        try:
            response = requests.get(f"{BACKEND_URL}/screenplays/open", params={
                "user_id": user_id,
                "project_id": project_id,
                "screenplay_name": screenplay_name
            })
        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502
        
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        
        SCRIPT = response.json().get('content')
        if not SCRIPT:
            return jsonify({'msg': 'Screenplay content not found'}), 404
        
        # Parse the XML screenplay content
        tree = ET.parse(SCRIPT)
        root = tree.getroot()

        # Extract style block (raw CSS)
        style_node = root.find('style')
        style = style_node.text if style_node is not None else ""

        # Extract smartType info
        smarttypes = {}
        smarttypenode = root.find('smartType')
        if smarttypenode is not None:
            for child in smarttypenode:
                component = child.get('component')
                if component:
                    # Get all text values inside <scene>, <time>, etc.
                    values = [elem.text.strip() for elem in child if elem.text]
                    smarttypes[component] = values

        # Extract content (screenplay body)
        content_node = root.find('content')
        content = []
        if content_node is not None:
            for elem in content_node:
                content.append({
                    "tag": elem.tag,       # e.g. "sceneHeading"
                    "class": elem.get("class"),
                    "text": (elem.text or "").strip()
                })

        return jsonify({
            "style": style,
            "smartTypes": smarttypes,
            "content": content
        })


    def save_screenplay():
        ...
    def delete_screenplay():
        ...

    @app.route('list_screenplays', methods=['GET'])
    @jwt_required()
    def list_screenplays():
        data = request.json 

        #gathering important metadata
        user_id = data.get('user_id') 
        project_id = data.get('project_id')

        if not all([user_id, project_id]):
            return jsonify({'msg': 'Missing required fields'}), 400
        try:
            response = requests.get(f"{BACKEND_URL}/screenplay/list", params={
                "user_id": user_id,
                "project_id": project_id
            })

            return response

        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502
        
    """
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)