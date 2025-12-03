from xml.etree import ElementTree as ET
import json


class Script():

    def __init__(self, StorageClass, DatabaseClass):
        #intializing storage system
        self.__storage = StorageClass

        #initializing database system
        self.__database = DatabaseClass

        self.__save: bool = False
        self.__file_content = None


    #BASIC CRUD SYSTEMS
    def __add_new_script(self, path, user, project, title, template):
        #adds entry to the database and creates the file in storage
        try:
            #adding entry to database
            dbscript = self.__database.add_script(owner_id=user, project_id=project, title=title, template=template)
        except Exception as e:
            raise e
            
        try:
            # Storing content as a JSON string
            self.__storage.put(path, json.dumps(self.__file_content), contenttype='application/json')
            self.__save = True
            return True
        except Exception as e:
            #deleting row from database if storage fails
            self.__database.delete_script(dbscript)
            raise e

    def create(self, content, title, user, project, template):
        #creates a new script both in storage and database
        path = f"users/{user}/scripts/{title}.lss"
        try:
            self.__file_content = content # Expecting a Python dictionary/list (from JSON)
            return self.__add_new_script(path, user, project, title, template)
        except Exception as e:
            raise e

    def open(self, title, user):
        #check if script exists in database
        script_exists = self.__database.get_script(title, user)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        #fetching from storage
        path = f"users/{user}/scripts/{title}.lss"
        try:
            response = self.__storage.get(path)
            file_content_str = response.get('Body').read().decode('utf-8')
            self.__file_content = json.loads(file_content_str) # Parse JSON string into object
        except Exception as e:
            raise e

    def quick_save(self, new_content):
        """In-memory update of the script's content."""
        self.__file_content = new_content


    def save(self, title, user, new_content):
        #saves/updates the file content in storage and database if necessary

        #make sure script exists in database
        script_exists = self.__database.get_script(title, user)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        
        # Update content in memory
        self.quick_save(new_content)

        #saving to storage
        path = f"users/{user}/scripts/{title}.lss"
        try:
            # Storing content as a JSON string
            self.__storage.put(path, json.dumps(self.__file_content), contenttype='application/json')
            self.__save = True
            return True
        except Exception as e:
            raise e

    def delete(self, title, user):
        #deletes script from both storage and database

        #make sure script exists in database
        script_exists = self.__database.get_script(title, user)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        
        #deleting from storage
        path = f"users/{user}/scripts/{title}.lss"
        try:
            self.__storage.delete(path)
        except Exception as e:
            raise e

        #deleting from database
        try:
            self.__database.delete_script(script_exists)
            return True
        except Exception as e:
            raise e
    
    def delete_project(self, user, project):
        #deletes all scripts associated with a project both from storage and database

        #fetching all scripts associated with the project
        scripts = self.__database.get_list_of_scripts(owner_id=user, project_id=project)
        
        for script in scripts:
            title = script.title
            #deleting from storage
            path = f"users/{user}/projects/{project}/scripts/{title}.lss"
            try:
                self.__storage.delete(path)
            except Exception as e:
                raise e

            #deleting from database
            try:
                self.__database.delete_script(script)
            except Exception as e:
                raise e
        return True
    
    #getters
    @property
    def file_content(self):
        """Provides read-only access to the private __file_content attribute."""
        return self.__file_content
