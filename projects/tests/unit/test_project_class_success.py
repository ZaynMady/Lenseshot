import pytest
from unittest.mock import MagicMock
import uuid
import json
from projects.common.Project import Project

@pytest.fixture
def project_handler():
    """Provides a Project instance with mocked dependencies."""
    mock_storage = MagicMock()
    mock_db = MagicMock()
    return Project(mock_storage, mock_db), mock_storage, mock_db

def test_create_project_success(project_handler):
    """
    Tests the successful creation of a new project.
    """
    handler, mock_storage, mock_db = project_handler
    owner_id = uuid.uuid4()
    project_name = "New Test Project"
    metadata = {"director": "Test Director", "title": project_name}
    new_project_id = uuid.uuid4()

    # Mock DB calls
    mock_db.list_projects.return_value = []
    mock_db.add_project.return_value = MagicMock(id=new_project_id)

    # Call the create method
    created_id = handler.create(owner_id, project_name, metadata)

    # Assertions
    assert created_id == new_project_id
    mock_db.list_projects.assert_called_once_with(owner_id)
    mock_db.add_project.assert_called_once_with(owner_id, project_name)
    
    expected_key = f"{owner_id}/projects/{new_project_id}/metadata.json"
    mock_storage.put.assert_called_once_with(expected_key, json.dumps(metadata))

def test_get_metadata_success(project_handler):
    """
    Tests successfully retrieving a project's metadata.
    """
    handler, mock_storage, mock_db = project_handler
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    metadata = {"title": "Test Project", "director": "John Doe"}
    metadata_json = json.dumps(metadata)

    # Mock DB and Storage calls
    mock_db.get_project.return_value = True  # Simulate project exists
    mock_storage.get.return_value = {
        'Body': MagicMock(read=lambda: metadata_json.encode('utf-8'))
    }

    # Call the get_metadata method
    retrieved_metadata = handler.get_metadata(user_id, project_id)

    # Assertions
    assert retrieved_metadata == metadata
    mock_db.get_project.assert_called_once_with(project_id, user_id)
    expected_key = f"{user_id}/projects/{project_id}/metadata.json"
    mock_storage.get.assert_called_once_with(expected_key)

def test_update_metadata_success(project_handler):
    """
    Tests successfully updating a project's metadata.
    """
    handler, mock_storage, mock_db = project_handler
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    new_metadata = {"title": "Updated Title", "producer": "Jane Smith"}

    # Mock DB call
    mock_db.get_project.return_value = True

    # Call the update_metadata method
    result = handler.update_metadata(user_id, project_id, new_metadata)

    # Assertions
    assert result is True
    mock_db.get_project.assert_called_once_with(project_id, user_id)
    expected_key = f"{user_id}/projects/{project_id}/metadata.json"
    mock_storage.put.assert_called_once_with(expected_key, json.dumps(new_metadata))

def test_list_projects_success(project_handler):
    """
    Tests successfully listing all projects for a user.
    """
    handler, mock_storage, mock_db = project_handler
    user_id = uuid.uuid4()
    
    # Mock project objects returned by the DB
    mock_project_1 = MagicMock(id=uuid.uuid4())
    mock_project_1.configure_mock(name="Project One")
    mock_project_2 = MagicMock(id=uuid.uuid4())
    mock_project_2.configure_mock(name="Project Two")
    mock_db.list_projects.return_value = [mock_project_1, mock_project_2]

    # Call the list_projects method
    projects = handler.list_projects(user_id)

    # Assertions
    assert len(projects) == 2
    assert projects[0].name == "Project One"
    assert projects[1].name == "Project Two"
    mock_db.list_projects.assert_called_once_with(user_id)

def test_delete_project_success(project_handler):
    """
    Tests the successful deletion of a project and its associated files.
    """
    handler, mock_storage, mock_db = project_handler
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()

    # Mock DB calls
    mock_db.get_project.return_value = True
    mock_db.delete_project.return_value = True

    # Mock Storage calls
    objects_to_delete = [
        {'Key': f"{user_id}/projects/{project_id}/metadata.json"},
        {'Key': f"{user_id}/projects/{project_id}/scripts/script1.lss"}
    ]
    mock_storage.list_objects.return_value = objects_to_delete

    # Call the delete_project method
    result = handler.delete_project(user_id, project_id)

    # Assertions
    assert result is True
    mock_db.get_project.assert_called_once_with(project_id, user_id)
    mock_db.delete_project.assert_called_once_with(project_id, user_id)

    prefix = f"{user_id}/projects/{project_id}/"
    mock_storage.list_objects.assert_called_once_with(prefix)
    
    expected_keys_to_delete = [obj['Key'] for obj in objects_to_delete]
    mock_storage.delete_many.assert_called_once_with(expected_keys_to_delete)