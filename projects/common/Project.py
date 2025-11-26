import json


class Project:
    def __init__(self, storage, db):
        self.__storage = storage
        self.__db = db
    
    def create(self, owner_id, project_name, metadata):
        #checking if project already exists
        existing_projects = self.__db.list_projects(owner_id)
        for proj in existing_projects:
            if proj.name == project_name:
                raise ValueError(f"Project with name '{project_name}' already exists.")
        #creating a new project in the database
        try:
            newproject = self.__db.add_project(owner_id, project_name)
        except Exception as e:
            raise Exception(f"Error creating project in database: {str(e)}")
        
        if newproject:
            try:
                #creating a path in storage for the project and storing the metadata as a json file in there
                key = f"users/{owner_id}/projects/{newproject.id}/metadata.json"
                self.__storage.put(key, json.dumps(metadata))
                return newproject.id
            except Exception as e:
                # Rollback DB entry if storage fails
                self.__db.delete_project(newproject.id, owner_id)
                raise e

    def delete_project(self, user_id, project_id):
        #logic to delete project from both database and 
        #checking if project exists in database
        try:
            project = self.__db.get_project(project_id, user_id)
            if not project:
                raise FileNotFoundError("Project not found.")
        except Exception as e:
            raise e
        
        # First, delete from storage
        try:
            prefix = f"users/{user_id}/projects/{project_id}/"
            #list all objects with the prefix
            objects_to_delete = self.__storage.list_objects(prefix)
            if objects_to_delete:
                keys = [obj['Key'] for obj in objects_to_delete]
                self.__storage.delete_many(keys)
        except Exception as e:
            # If storage fails, we don't proceed to delete from the DB
            raise Exception(f"Error deleting project from storage: {str(e)}")

        # Then, delete from the database
        try:
            self.__db.delete_project(project_id, user_id)
        except Exception as e:
            # This is a tricky state. Storage is gone, but DB record remains.
            # For now, we just raise the error.
            raise Exception(f"Error deleting project from database: {str(e)}")

        return True
 
    def update_metadata(self, user_id, project_id, metadata):
        #checking if project exists in database
        try:
            project = self.__db.get_project(project_id, user_id)
            if not project:
                raise FileNotFoundError("Project not found.")
        except Exception as e:
            raise e
        
        key = f"users/{user_id}/projects/{project_id}/metadata.json"
        try:
            self.__storage.put(key, json.dumps(metadata))
        except Exception as e:
            raise e
        return True
    

    def get_metadata(self,user_id, project_id):
        key = f"users/{user_id}/projects/{project_id}/metadata.json"
        #checking if project exists in database
        try:
            project = self.__db.get_project(project_id, user_id)
            if not project:
                raise FileNotFoundError("Project not found.")
        except Exception as e:
            raise e
        
        try:
            response = self.__storage.get(key)
            if not response:
                raise FileNotFoundError("Metadata file not found in storage.")
            metadata_content = response['Body'].read().decode('utf-8')
            metadata = json.loads(metadata_content)
            return metadata
        except Exception as e:
            raise e
    
    def list_projects(self, user_id):
        try:
            projects = self.__db.list_projects(user_id)
            return projects
        except Exception as e:
            raise Exception(f"Error listing projects from database: {str(e)}")