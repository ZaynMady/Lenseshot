import pytest
import json
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET
from scripts.common.Script import Script
import uuid

# A mock JSON content for use in tests
mock_content = [
    {"class": "scene-heading", "content": "INT. ROOM - DAY"},
    {"class": "action", "content": "A test is run."}
]

#testing create a new screenplay function 
def test_create_new_script_success():
    """
        Tests that the function can successfuly create a screenplay as expected
    """

    mock_storage = MagicMock()
    mock_db = MagicMock()
    mock_db.add_script.return_value = MagicMock() # Simulate successful DB add

    script = Script(mock_storage, mock_db)
    userid = MagicMock()
    projectid = MagicMock()

    newscript = script.create(mock_content, "Godfather", userid, projectid, "american_screenplay")

    assert newscript == True
    #asserting file content is equal to the template being parsed
    assert script.file_content == mock_content
    mock_storage.put.assert_called_once_with(f"users/{userid}/scripts/Godfather.lss", json.dumps(mock_content), contenttype='application/json')

def test_open_script_success():
    """
    Tests that a script can be successfully opened and its content parsed.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = MagicMock()
    title = "My Script"

    # Mock the database to confirm the script exists
    mock_db.get_script.return_value = True
    # Mock storage to return the file content
    mock_storage.get.return_value = {'Body': MagicMock(read=lambda: json.dumps(mock_content).encode('utf-8'))}
    
    script = Script(mock_storage, mock_db)
    script.open(title, userid)

    # Assert that the script's properties are populated correctly
    assert script.file_content == mock_content

    # Verify that the mocks were called correctly
    mock_db.get_script.assert_called_once_with(title, userid)
    mock_storage.get.assert_called_once_with(f"users/{userid}/scripts/{title}.lss")

def test_quick_save_success():
    """
    Tests that quick_save updates the in-memory content of the script.
    """
    script = Script(MagicMock(), MagicMock())
    new_content = [{'class': 'scene-heading', 'content': 'A NEW SCENE'}]
    script.quick_save(new_content)

    # quick_save updates the internal __file_content, not __content
    assert script.file_content == new_content

def test_save_script_success():
    """
    Tests that a script's modified content is correctly saved to storage.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()
    title = "My Script"

    # Mock DB and initial storage 'get' call
    mock_db.get_script.return_value = True

    script = Script(mock_storage, mock_db)

    # New content to save
    new_content = [
        {'class': 'scene-heading', 'content': 'INT. OFFICE - NIGHT'}
    ]

    result = script.save(title, userid, new_content)

    assert result is True
    # Check that storage.put was called
    mock_storage.put.assert_called_once_with(f"users/{userid}/scripts/{title}.lss", json.dumps(new_content), contenttype='application/json')

def test_delete_script_success():
    """
    Tests that a script is deleted from both storage and the database.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = MagicMock()
    title = "Script to Delete"
    mock_script_obj = MagicMock()

    mock_db.get_script.return_value = mock_script_obj

    script = Script(mock_storage, mock_db)
    result = script.delete(title, userid)

    assert result is True
    mock_storage.delete.assert_called_once_with(f"users/{userid}/scripts/{title}.lss")
    mock_db.delete_script.assert_called_once_with(mock_script_obj)

def test_delete_project_success():
    """
    Tests that all scripts associated with a project are deleted.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()

    # Mock the list of scripts to be returned by the database
    script1 = MagicMock(title="Script1")
    script2 = MagicMock(title="Script2")
    mock_db.get_list_of_scripts.return_value = [script1, script2]

    script = Script(mock_storage, mock_db)
    result = script.delete_project(userid, projectid)

    assert result is True
    mock_db.get_list_of_scripts.assert_called_once_with(owner_id=userid, project_id=projectid)
    assert mock_storage.delete.call_count == 2
    assert mock_db.delete_script.call_count == 2
    mock_storage.delete.assert_any_call(f"users/{userid}/projects/{projectid}/scripts/Script1.lss")
    mock_storage.delete.assert_any_call(f"users/{userid}/projects/{projectid}/scripts/Script2.lss")
    mock_db.delete_script.assert_any_call(script1)
    mock_db.delete_script.assert_any_call(script2)
