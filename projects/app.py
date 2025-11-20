from flask import Flask 
from flask_cors import CORS
from flask import jsonify, request, json
from utilities.auth import supabase_jwt_required, get_current_user_id
from utilities.cloudflareStorage import Cloudflare
import os
from dotenv import load_dotenv
from models import db, Project





def create_app():
    load_dotenv()
    app = Flask(__name__)

    #loading environment variables
    CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    CLOUDFLARE_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_ACCESS_KEY_ID")
    CLOUDFLARE_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY")
    CLOUDFLARE_BUCKET_NAME = os.getenv("CLOUDFLARE_BUCKET_NAME")

    SUPABASE_SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")

    DATABASE_URI = os.getenv("DATABASE_URL")

    #loading configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    #setting up database
    db.init_app(app)
    
    #Enable CORS for the app
    CORS(app, 
    supports_credentials=True,
    resources={r"/api/*": {"origins": ["http://localhost:5173", 
                                        "http://localhost:5000"]}}) #Enable CORS for the app

    #setting up utility objects
    Storage = Cloudflare(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)
    #Basic CRUD

    @app.route(f'/api/projects/create', methods=['POST', 'OPTIONS'])
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
        
        #getting the user id from the token 
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        current_user = get_current_user_id(SUPABASE_SECRET_KEY, token)[0]

        #checking if project already exists
        existing = Project.query.filter_by(owner=current_user, name=project_title).first()
        if existing:
            return jsonify({"message": "Project with this name already exists"}), 400

        #Saving Project to database
        try:
            project = Project(owner=current_user, name=project_title)   
            db.session.add(project)        
            db.session.commit()
        except Exception as e:
            return jsonify({"message": f"Failed to save project to database: {str(e)}"}), 500

        project_id = project.id

        #creating a filepath for the new project
        project_path = f'users/{current_user}/projects/{project_id}'

        #uploading the metadata to cloud storage
        try:
            Storage.put(
                Bucket=CLOUDFLARE_BUCKET_NAME,
                Key=f'{project_path}/metadata.json',
                Body=json.dumps(project_metadata),
                ContentType='application/json'
                )
            return jsonify({"message": "Project created successfully", "project_id": project_id}), 201
        except Exception as e:
            return jsonify({"message": f"Failed to create project: {str(e)}"}), 500

    @app.route(f'/api/projects/<uuid:projectid>/metadata', methods=['OPTIONS', 'GET'])
    @supabase_jwt_required
    def metadata_project(projectid):
        if request.method == 'OPTIONS':
            return "", 200

        if request.method == 'GET':
        #getting the user id from the token
            auth_header = request.headers.get('Authorization', None)
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ")[1] 
            current_user = get_current_user_id(SUPABASE_SECRET_KEY, token)[0]

            #checking if project exists
            project = Project.query.filter_by(id=projectid, owner=current_user).first()
            if not project:
                return jsonify({"message": "Project not found"}), 404


            #creating a filepath for the new project
            project_path = f'users/{current_user}/projects/{projectid}'
            metadata_file_path = f'{project_path}/metadata.json'

            try:
                #downloading the metadata from the storage bucket
                key = metadata_file_path
                response = Storage.get(bucket=CLOUDFLARE_BUCKET_NAME, key=key)
                metadata_content = response['Body'].read().decode('utf-8')
                data = json.loads(metadata_content)
                return jsonify(data), 200
            
            except Exception as e:
                return jsonify({"message": f"Failed to retrieve metadata: {str(e)}"}), 500
            
    @app.route(f'/api/projects/<uuid:projectid>', methods=['DELETE'])
    @supabase_jwt_required
    def delete_project(projectid):
        #getting the user id from the token 
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1] 
        current_user = get_current_user_id(SUPABASE_SECRET_KEY, token)[0]

        #checking if project exists
        project = Project.query.filter_by(id=projectid, owner=current_user).first()
        if not project:
            return jsonify({"message": "Project not found"}), 404

        #creating a filepath for the new project
        project_path = f'users/{current_user}/projects/{projectid}'

        try:
            #deleting all files in the project directory
            objects_to_delete = Storage.list_files(bucket=CLOUDFLARE_BUCKET_NAME, prefix=f'{project_path}/')
            if objects_to_delete:
                Storage.delete_many(bucket=CLOUDFLARE_BUCKET_NAME, keys=objects_to_delete)

            #deleting the project from the database
            db.session.delete(project)
            db.session.commit()

            return jsonify({"message": "Project deleted successfully"}), 200
        except Exception as e:
            return jsonify({"message": f"Failed to delete project: {str(e)}"}), 500

    @app.route(f'/api/projects/<uuid:projectid>/metadata', methods=['OPTIONS', 'PUT'])
    @supabase_jwt_required
    def update_metadata(projectid):
        if request.method == 'OPTIONS':
            return "", 200

        if request.method == 'PUT':
            #getting the user id from the token 
            auth_header = request.headers.get('Authorization', None)
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ")[1] 
            current_user = get_current_user_id(SUPABASE_SECRET_KEY, token)[0]

            #checking if project exists
            project = Project.query.filter_by(id=projectid, owner=current_user).first()
            if not project:
                return jsonify({"message": "Project not found"}), 404

            new_metadata = request.json.get('metadata', {})
            if not new_metadata:
                return jsonify({"message": "Metadata is required"}), 400

    

            #creating a filepath for the new project
            project_path = f'users/{current_user}/projects/{projectid}'
            metadata_file_path = f'{project_path}/metadata.json'

            try:
                #downloading the existing metadata from the storage bucket
                key = metadata_file_path
                response = Storage.get(bucket=CLOUDFLARE_BUCKET_NAME, Key=key)
                metadata_content = response['Body'].read().decode('utf-8')
                existing_metadata = json.loads(metadata_content)

                #updating the metadata
                existing_metadata.update(new_metadata)

                #uploading the updated metadata back to the storage bucket
                Storage.put(
                    bucket=CLOUDFLARE_BUCKET_NAME,
                    key=metadata_file_path,
                    body= json.dumps(existing_metadata),
                    contenttype='application/json'
                )
                return jsonify({"message": "Metadata updated successfully"}), 200

            except Exception as e:
                return jsonify({"message": f"Failed to update metadata: {str(e)}"}), 500
    
    @app.route('/api/projects/list', methods=['GET', 'OPTIONS'])
    @supabase_jwt_required
    def list_projects():
        if request.method == 'OPTIONS':
            return "", 200

        if request.method == 'GET':
            #getting the user id from the token 
            auth_header = request.headers.get('Authorization', None)
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Missing or invalid Authorization header"}), 401

            token = auth_header.split(" ")[1] 
            current_user = get_current_user_id(SUPABASE_SECRET_KEY, token)[0]

            try:
                projects = Project.query.filter_by(owner=current_user).all()

                if projects: 
                    storage_client = create_client(CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ACCESS_KEY_ID, CLOUDFLARE_SECRET_ACCESS_KEY)
                    bucket_name = CLOUDFLARE_BUCKET_NAME

                    #creating a list of jsons for metadata of each project
                    metadata_list = []
                    for project in projects:
                        project_path = f'users/{current_user}/projects/{project.id}'
                        metadata_file_path = f'{project_path}/metadata.json'
                        try:
                            response = storage_client.get_object(Bucket=bucket_name, Key=metadata_file_path)
                            metadata_content = response['Body'].read().decode('utf-8')
                            metadata = json.loads(metadata_content)
                            metadata["project_id"] = project.id
                            metadata_list.append(metadata)
                        except Exception as e:
                            return jsonify({"msg": "issue with storage cloudflare", "error" : str(e)}), 890
                    return jsonify(metadata_list), 201
                    
                        
                    
            except Exception as e:
                return jsonify({"message": f"Failed to retrieve projects: {str(e)}"}), 500
    
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=7000, debug=True)