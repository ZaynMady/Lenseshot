import pytest
from unittest.mock import MagicMock
import uuid
from projects.common.Project import Project

@pytest.fixture
def project_handler():
    """Provides a Project instance with mocked dependencies."""
    mock_storage = MagicMock()
    mock_db = MagicMock()
    return Project(mock_storage, mock_db), mock_storage, mock_db

# --- Create Method Failures ---

def test_create_project_already_exists(project_handler):
    """
    Tests that create raises a ValueError if a project with the same name already exists.
    """
    handler, mock_storage, mock_db = project_handler
    owner_id = uuid.uuid4()
    project_name = "Existing Project"
    
    # Mock DB to return an existing project
    mock_project = MagicMock()
    mock_project.configure_mock(name=project_name)
    mock_db.list_projects.return_value = [mock_project]
    
    with pytest.raises(ValueError, match=f"Project with name '{project_name}' already exists."):
        handler.create(owner_id, project_name, {})
        
    mock_db.add_project.assert_not_called()
    mock_storage.put.assert_not_called()

def test_create_project_db_add_failure(project_handler):
    """
    Tests that create raises an exception if the database add_project call fails.
    """
    handler, mock_storage, mock_db = project_handler
    owner_id = uuid.uuid4()
    
    mock_db.list_projects.return_value = []
    mock_db.add_project.side_effect = Exception("DB connection failed")
    
    with pytest.raises(Exception, match="DB connection failed"):
        handler.create(owner_id, "New Project", {})
        
    mock_storage.put.assert_not_called()

def test_create_project_storage_failure_and_rollback(project_handler):
    """
    Tests that create raises an exception if storage fails, and that the DB entry is rolled back.
    """
    handler, mock_storage, mock_db = project_handler
    owner_id = uuid.uuid4()
    new_project_id = uuid.uuid4()
    mock_project_obj = MagicMock(id=new_project_id)

    mock_db.list_projects.return_value = []
    mock_db.add_project.return_value = mock_project_obj
    mock_storage.put.side_effect = Exception("Cloudflare R2 is down")

    with pytest.raises(Exception, match="Cloudflare R2 is down"):
        handler.create(owner_id, "New Project", {})

    # Assert that the rollback function was called
    mock_db.delete_project.assert_called_once_with(new_project_id, owner_id)

# --- Get/Update Metadata Failures ---

def test_get_metadata_project_not_found(project_handler):
    """
    Tests that get_metadata raises FileNotFoundError if the project is not in the database.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = None

    with pytest.raises(FileNotFoundError, match="Project not found"):
        handler.get_metadata(uuid.uuid4(), uuid.uuid4())
    
    mock_storage.get.assert_not_called()

def test_get_metadata_storage_failure(project_handler):
    """
    Tests that get_metadata raises an exception if the storage call fails.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = True
    mock_storage.get.side_effect = Exception("Storage get failed")

    with pytest.raises(Exception, match="Storage get failed"):
        handler.get_metadata(uuid.uuid4(), uuid.uuid4())

def test_update_metadata_project_not_found(project_handler):
    """
    Tests that update_metadata raises FileNotFoundError if the project is not in the database.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = None

    with pytest.raises(FileNotFoundError, match="Project not found"):
        handler.update_metadata(uuid.uuid4(), uuid.uuid4(), {})

    mock_storage.put.assert_not_called()

# --- List Projects Failures ---

def test_list_projects_db_failure(project_handler):
    """
    Tests that list_projects raises an exception if the database call fails.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.list_projects.side_effect = Exception("DB list failed")

    with pytest.raises(Exception, match="DB list failed"):
        handler.list_projects(uuid.uuid4())

# --- Delete Project Failures ---

def test_delete_project_not_found(project_handler):
    """
    Tests that delete_project raises FileNotFoundError if the project is not in the database.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = None

    with pytest.raises(FileNotFoundError, match="Project not found"):
        handler.delete_project(uuid.uuid4(), uuid.uuid4())

    mock_storage.list_objects.assert_not_called()
    mock_storage.delete_many.assert_not_called()
    mock_db.delete_project.assert_not_called()

def test_delete_project_storage_list_failure(project_handler):
    """
    Tests that delete_project raises an exception if listing storage objects fails.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = True
    mock_storage.list_objects.side_effect = Exception("Storage list failed")
    
    with pytest.raises(Exception, match="Error deleting project from storage: Storage list failed"):
        handler.delete_project(uuid.uuid4(), uuid.uuid4())
    
    mock_storage.delete_many.assert_not_called()
    mock_db.delete_project.assert_not_called()

def test_delete_project_db_delete_failure(project_handler):
    """
    Tests that delete_project raises an exception if the database deletion fails.
    Note: In the current design, storage objects would have already been deleted.
    """
    handler, mock_storage, mock_db = project_handler
    mock_db.get_project.return_value = True
    mock_storage.list_objects.return_value = [{'Key': 'some/key'}] # Simulate that storage has objects
    mock_db.delete_project.side_effect = Exception("DB delete failed")

    with pytest.raises(Exception, match="DB delete failed"):
        handler.delete_project(uuid.uuid4(), uuid.uuid4())

    # Verify that the storage deletion was still attempted before the DB failure
    mock_storage.delete_many.assert_called_once_with(['some/key'])