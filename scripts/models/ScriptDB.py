from utilities.database import Database
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from .ScriptModel import ScriptsModel, ScenesModel
import uuid


class ScriptDB(Database):
    def __init__(self, database_url):
        super().__init__(database_url)

    def add_script(self, title, owner_id, project_id):
        new_script = ScriptsModel(
            id=uuid.uuid4(),
            title=title,
            owner_id=owner_id,
            project_id=project_id
        )
        self._session.add(new_script)
        self._session.commit()
        #optional return the created script
        return new_script
    
    def get_script(self, script_title, owner_id, project_id):
        return self._session.query(ScriptsModel).filter_by(
            title=script_title,
            owner_id=owner_id,
            project_id=project_id
        ).first()
    
    def update_script_title(self, script, new_title):
        script.title = new_title
        self._session.commit()

    def delete_script(self, script):
        self._session.delete(script)
        self._session.commit()
        
    def get_list_of_scripts(self, owner_id, project_id):
        return self._session.query(ScriptsModel).filter_by(
            owner_id=owner_id,
            project_id=project_id
        ).all()