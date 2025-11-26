from xml.etree import ElementTree as ET
import json

class Script():

    @staticmethod
    def __load_tag_map(root: ET.Element):
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

    @staticmethod
    def __json_to_xml(data, tag_map):
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
            else:
                raise ValueError(f"No tag found for class: {class_name}")
        updated_script = f"<content>\n{updated_script}</content>"
        updated_script = ET.fromstring(updated_script)
        return updated_script

    
    def __init__(self, StorageClass, DatabaseClass):
        #intializing storage system
        self.__storage = StorageClass

        #initializing database system
        self.__database = DatabaseClass

        self.__save: bool = False
        self.__content = []
        self.__components = []
        self.__style = ""
        self.__smarttypes = {}
        self.__file_content = None


    def __init_xml(self, xml_content):
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            # __init__ should raise an exception, not return a value.
            raise ValueError(f"Invalid XML format: {e}") from e

        self.__file_content = xml_content
        #Extracting tag_map
        self.tag_map = Script.__load_tag_map(root)

        #Extracting Components
        self.__components = list(self.tag_map.values())
        # Extract style (full raw text)
        style_node = root.find('style')
        if style_node is not None:
            # Join all text nodes and normalize whitespace
            self.__style = "\n".join(line.strip() for line in style_node.itertext() if line.strip())
        else:
            self.__style = ""


        # Extract smartType info
        self.__smarttypes = {}
        smarttypenode = root.find('smartType')
        if smarttypenode is not None:
            for child in smarttypenode:
                component = child.get('component')
                if component:
                    values = [elem.text.strip() for elem in child if elem.text]
                    self.__smarttypes[component] = values

        # Extract content
        content_node = root.find('content')
        self.__content = []
        if content_node is not None:
            for elem in content_node:
                self.__content.append({
                    "tag": elem.tag,
                    "class": self.tag_map.get(elem.tag, ""),
                    "content": (elem.text or "").strip()
                })


    #BASIC CRUD SYSTEMS
    def __add_new_script(self, path, user, project, title):
        #adds entry to the database and creates the file in storage
        try:
            #adding entry to database
            dbscript = self.__database.add_script(owner_id=user, project_id=project, title=title)
        except Exception as e:
            raise e
            
        try:
            self.__storage.put(path, self.__file_content)
            self.__save = True
            return True
        except Exception as e:
            #deleting row from database if storage fails
            self.__database.delete_script(dbscript)
            raise e

    def create(self, content, title, user, project):
        #creates a new script both in storage and database
        path = f"users/{user}/projects/{project}/scripts/{title}.lss"
        try:
            self.__init_xml(content)
            return self.__add_new_script(path, user, project, title)
        except Exception as e:
            raise e

    def open(self, title, user, project):
        #check if script exists in database
        script_exists = self.__database.get_script(title, user, project)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        #fetching from storage
        path = f"users/{user}/projects/{project}/scripts/{title}.lss"
        try:
            response = self.__storage.get(path)
            file_content = response.get('Body').read().decode('utf-8')
        except Exception as e:
            raise e
        
        try:
            self.__init_xml(file_content)
        except Exception as e:
            raise e


    def quick_save(self, new_content : json):
        #saves/updates the file content in storage
        
        #append self.content to new screenplay content
        try:
            self.__content = new_content
        except Exception as e:
            raise e
    
    def save(self, title, user, project, new_content : json):
        #saves/updates the file content in storage and database if necessary

        #make sure script exists in database
        script_exists = self.__database.get_script(title, user, project)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        
        #make sure script exists in storage
        path = f"users/{user}/projects/{project}/scripts/{title}.lss"
        try:
            self.__storage.get(path)
        except Exception as e:
            raise e

        #append self.content to new screenplay content
        try:
            self.quick_save(new_content)
        except Exception as e:
            raise e
        
        #updating script in storage

        #saving to storage
        path = f"users/{user}/projects/{project}/scripts/{title}.lss"
        try:
            # Parse the original file content to preserve structure
            root = ET.fromstring(self.__file_content)
            # Find the content node, clear it, and extend it with the new XML content
            root.find('content').clear()

            xml_elements_content = self.__json_to_xml(self.__content, self.tag_map)

            root.find('content').extend(list(xml_elements_content))
            
            self.__file_content = ET.tostring(root, encoding='unicode')

            self.__storage.put(path, self.__file_content)
            self.__save = True
            return True
        except Exception as e:
            raise e

    def delete(self, title, user, project):
        #deletes script from both storage and database

        #make sure script exists in database
        script_exists = self.__database.get_script(title, user, project)
        if not script_exists:
            raise FileNotFoundError("Script does not exist in database.")
        
        #deleting from storage
        path = f"users/{user}/projects/{project}/scripts/{title}.lss"
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
    @property
    def components(self):
        """Provides read-only access to the private __components attribute."""
        return self.__components
    @property
    def style(self):
        """Provides read-only access to the private __style attribute."""
        return self.__style

    @property
    def smarttypes(self):
        """Provides read-only access to the private __smarttypes attribute."""
        return self.__smarttypes

    @property
    def content(self):
        """Provides read-only access to the private __content attribute."""
        return self.__content
