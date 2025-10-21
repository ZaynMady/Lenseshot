from logging import root
from flask import Flask, request, jsonify
import os
import requests
from xml.etree import  ElementTree as ET
from flask_cors import CORS
from utilities.auth import get_current_user_id, supabase_jwt_required
from utilities.storage import create_client, list_files
from dotenv import load_dotenv




def create_app():

    app = Flask(__name__)
    load_dotenv()

    #loading environmental variables
    CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
    CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
    
    #Enable CORS for the app
    CORS(app, 
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}}) 

    
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
    @supabase_jwt_required
    def create_screenplay():
        #Handling an Options request 
        if request.method == "OPTIONS":
            return "", 200 
        
        #extracting the request body and headers
        data = request.json
        auth_header = request.headers.get("Authorization", None)

        #geting the current user_id
        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401
        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_JWT_SECRET, token)[0]

        #extracting important information necessary to create a screenplay
        template_name = data.get('template_name')       
        screenplay_name = data.get('screenplay_name')   
        project_id = data.get('project_id')             

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

        #creating key_path
        script_key = f"users/{current_user}/projects/{project_id}/screenplays/{screenplay_name}.lss"


        try:
            #sending the newly created file to Cloudflare storage
            r3_client = create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)

            r3_client.put_object(Key=script_key,Bucket= CLOUDFLARE_BUCKET_NAME, Body=template_content)

            return jsonify({"msg" : "Screenplay Created Successfully"}), 200
             
        except Exception as e:
            return jsonify({'msg': 'storage connection failed', 'error': str(e)}), 502

    
    @app.route('/api/open_screenplay', methods=['GET', 'POST', 'OPTIONS'])
    def open_screenplay():
        if request.method == "OPTIONS":
            return "", 200

        #getting requested data and headers
        data = request.json
        auth_header = request.headers.get("Authorization", None)

        #getting user ID
        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401

        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_JWT_SECRET, token)[0]

        #getting screenplay data from request necessary to find the file
        screenplay_name = data.get('screenplay_name')   
        project_id = data.get('project_id')             

        if not all([screenplay_name, project_id]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        try:
            #Screenplay key 
            script_key = f"users/{current_user}/projects/{project_id}/screenplays/{screenplay_name}"
            #Storage client connection
            r3_client = create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)
            response = r3_client.get_object(Key=script_key,Bucket=CLOUDFLARE_BUCKET_NAME )
        except Exception as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

        
        SCRIPT = response['Body'].read().decode('utf-8')
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

        if not auth_header: 
            return jsonify({'msg': 'Missing Auth Header'}), 405
        
        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_JWT_SECRET, token)[0]

        if not all([project_id]):
            return jsonify({'msg': 'Missing required fields'}), 400
        try:
            screenplays_key = f"users/{current_user}/projects/{project_id}/screenplays"

            r3_client = create_client(
                CLOUDFLARE_ACCOUNT_ID,
                CLOUDFLARE_ACCESS_KEY_ID,
                CLOUDFLARE_SECRET_ACCESS_KEY
            )
            screenplay_list = list_files(r3_client, CLOUDFLARE_BUCKET_NAME, screenplays_key, ".lss")

            response = jsonify({"screenplays": screenplay_list})
            return response, 200

        except Exception as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502

    @app.route('/api/save_screenplay', methods=['POST', 'OPTIONS', 'GET'])  
    def save_screenplay():
        if request.method == "OPTIONS":
            return "", 200 
        data = request.json
        auth_header = request.headers.get("Authorization", None)
        
        #getting user_id
        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401
        
        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_JWT_SECRET, token)[0]

        #getting important screenplay data
        screenplay_Json = data.get('screenplay')      
        screenplay_name = data.get('screenplay_name')
        project_id = data.get('project_id')
        if not all([screenplay_Json, screenplay_name, project_id]):
            return jsonify({'msg': 'Missing required fields', "response": request.json}), 400

        #getting the last upated version of the screenplay 
        try:
            r3_client = create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)
            screenplay_key = f"users/{current_user}/projects/{project_id}/screenplays/{screenplay_name}"
            r3_response = r3_client.get_object(Key=screenplay_key, Bucket=CLOUDFLARE_BUCKET_NAME) 
        except Exception as e:
            return jsonify({"msg" : "Couldn't fetch previous screenplay", "error": str(e)}), 406
        
        prev_script = r3_response["Body"].read().decode("utf-8")
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
        try:
            r3_client.put_object(Key=screenplay_key, Bucket=CLOUDFLARE_BUCKET_NAME, Body=screenplay_content)
        except Exception as e:
            return jsonify({'msg': 'Storage_connection failed', 'error': str(e)}), 502

        return jsonify({"msg" : "Screenplay Saved Successfully"}), 200     

    @app.route('/api/delete_screenplay', methods=['POST', 'OPTIONS', 'GET'])
    def delete_screenplay():
        if request.method == "OPTIONS":
            return "", 200
        #getting data from frontend
        data = request.json 

        #extracting relevant information from data
        screenplay_name = data.get('screenplay_name')
        project_id = data.get('project_id')

        if not all ([screenplay_name, project_id]):
            return jsonify({'msg': "Missing required fields"}), 400

        #sending required headers
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"msg": "Missing Authorization Header"}), 401
        
        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_JWT_SECRET, token)[0]

        #sending a request to the backend to delete the screenplay
        try: 
            r3_client = create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)
            screenplay_key = f"users/{current_user}/projects/{project_id}/screenplays/{screenplay_name}"
            r3_client.delete_object(Key=screenplay_key, Bucket=CLOUDFLARE_BUCKET_NAME)
            return jsonify({"msg": "Screenplay Deleted Successfully"}), 200
        except Exception as e:
            return jsonify({'msg': 'Backend connection failed', 'error': str(e)}), 502
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000 , debug=True)