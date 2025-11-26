from utilities.database import Database
from .models import Project
import uuid

class ProjectDb(Database):
    #initializes a connection
    def __init__(self, database_url):
        super().__init__(database_url)
    
    #method to add a new project
    def add_project(self, owner_id, project_name):
        new_project = Project(
            id=uuid.uuid4(),
            owner=owner_id,
            name=project_name
        )
        self._session.add(new_project)
        self._session.commit()
        return new_project
        
    #method to delete a project
    def delete_project(self, project_id, user_id):
        project = self._session.query(Project).filter_by(
            id=project_id, 
            owner=user_id
            ).first()
        self._session.delete(project)
        self._session.commit(
        )
        return True
        
    #method to update project metadata
    def update_project_name(self, project_id, new_name):
        project = self._session.query(Project).filter_by(
            id=project_id
        ).first()
        project.name = new_name
        self._session.commit()
        return True

    #method to get project name
    def get_project(self, project_id, owner_id):
        project = self._session.query(Project).filter_by(
            id=project_id,
            owner=owner_id
        ).first()
        return project.id if project else None
    
    #method to list projects under a user id
    def list_projects(self, owner_id):
        return self._session.query(Project).filter_by(
            owner=owner_id
        ).all()
    
    

    