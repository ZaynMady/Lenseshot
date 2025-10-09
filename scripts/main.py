from logging import root
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

    
    def load_tag_map(root : ET.Element):
        tag_map = {}
        try:

            #finding the component node
            component_node = root.find('components')

            for child in component_node:
                tag = child.tag
                class_name = child.get('class')
                if tag and class_name:
                    tag_map[tag] = class_name
        except Exception as e:
            print(f"Error loading tag map: {e}")
        return tag_map

    def json_to_xml(data, tag_map):
        #establishing a base string
        updated_script = ""
        #building the algorithm model assuming data is a list of dictionaries "class" : "content"
        for line in data: 
            class_name = line.get('class')
            content = line.get('content')
            #finding the corresponding tag for the class
            tag = None
            for t, c in tag_map.items():
                if c == class_name:
                    tag = t
                    break
            if tag:
                updated_script += f"<{tag}>{content}</{tag}>\n"
        return updated_script




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

    
    @app.route('/api/open_screenplay', methods=['GET', 'POST', 'OPTIONS'])
    def open_screenplay():
        if request.method == "OPTIONS":
            return "", 200
    
        data = request.json
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        headers = {"content-type": "application/json"}
        headers["Authorization"] = auth_header


        screenplay_name = data.get('screenplay_name')   # e.g., "MyFirstScript"
        project_id = data.get('project_id')             # e.g., "123"               # comes from JWT

        if not all([screenplay_name, project_id]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        try:
            body = {


                "project_id": project_id,
                "screenplay_name": screenplay_name
            }
            response = requests.get(f"{BACKEND_URL}/screenplay/open", json=body, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        
        SCRIPT = response.json().get('content')
        if not SCRIPT:
            return jsonify({'msg': 'Screenplay content not found'}), 404

        try:
            root = ET.fromstring(SCRIPT)
        except ET.ParseError as e:
            return jsonify({'msg': 'Invalid XML format', 'error': str(e)}), 400

        #Extracting tag_map
        tag_map = load_tag_map(root)

        #Extracting Components
        components = list(tag_map.values())
        # Extract style (full raw text)
        style_node = root.find('style')
        if style_node is not None:
            # Join all text nodes and normalize whitespace
            style = "\n".join(line.strip() for line in style_node.itertext() if line.strip())
        else:
            style = ""


        # Extract smartType info
        smarttypes = {}
        smarttypenode = root.find('smartType')
        if smarttypenode is not None:
            for child in smarttypenode:
                component = child.get('component')
                if component:
                    values = [elem.text.strip() for elem in child if elem.text]
                    smarttypes[component] = values

        # Extract content
        content_node = root.find('content')
        content = []
        if content_node is not None:
            for elem in content_node:
                content.append({
                    "tag": elem.tag,
                    "class": tag_map.get(elem.tag, ""),
                    "content": (elem.text or "").strip()
                })

        return jsonify({
            "style": style,
            "smartTypes": smarttypes,
            "content": content,
            "components": components
        })

    @app.route('/api/list_screenplays', methods=['GET', 'POST', 'OPTIONS'])
    def list_screenplays():
        if request.method == "OPTIONS":
            return "", 200
        data = request.json 

        #gathering important metadata
        project_id = data.get('project_id')
        auth_header = request.headers.get("Authorization", None)

        headers = {"content-type": "application/json"}
        headers["Authorization"] = auth_header

        if not all([project_id]):
            return jsonify({'msg': 'Missing required fields'}), 400
        try:
            body = {
                "project_id": project_id
            }
            response = requests.get(f"{BACKEND_URL}/screenplay/list",headers=headers ,json=body)

            return jsonify(response.json()), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

    @app.route('/api/save_screenplay', methods=['POST', 'OPTIONS', 'GET'])  
    def save_screenplay():
        if request.method == "OPTIONS":
            return "", 200 
        data = request.json
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        headers = {"content-type": "application/json"}
        headers["Authorization"] = auth_header

        screenplay_Json = data.get('screenplay')      
        screenplay_name = data.get('screenplay_name')
        project_id = data.get('project_id')
        if not all([screenplay_Json, screenplay_name, project_id]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        #getting the last upated version of the screenplay 
        response = requests.get(f"{BACKEND_URL}/screenplay/open", json={
            "screenplay_name": screenplay_name,
            "project_id": project_id
        }, headers=headers)
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        
        prev_script = response.json().get('content')
        if not prev_script:
            return jsonify({'msg': 'Previous screenplay content not found'}), 404
        
        try: 
            root = ET.fromstring(prev_script) #establishing the root element
            tag_map = load_tag_map(root) #loading tag map to switch between classes and tags
            updated_script = json_to_xml(screenplay_Json, tag_map) #converting json back to xml
            updated_xml = f"<content>\n{updated_script}</content>"  #wrapping content in content tag
            #parsing the updated content to ensure it's well-formed XML
            updated_content_element = ET.fromstring(updated_xml)
            #updating the root element with the new content 
            root.find('content').clear()
            root.find('content').extend(updated_content_element)
            screenplay_content = ET.tostring(root, encoding="unicode")
        except ET.ParseError as e:
            return jsonify({'msg': 'Invalid XML format', 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'msg': 'Error processing screenplay', 'error': str(e)}), 500

        # Forward to backend microservice
        payload = {
            "content": screenplay_content,
            "screenplay_name": screenplay_name,
            "project_id": project_id
        }

        try:
            response = requests.post(f"{BACKEND_URL}/screenplay/save", json=payload, headers=headers)
        except requests.exceptions.RequestException as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

        return jsonify(response.json()), response.status_code      

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)