import pytest
from unittest.mock import MagicMock
from scripts.common.Script import Script
import uuid

# A valid XML template for use in tests
mock_template = """<?xml version="1.0" encoding="UTF-8"?>
<template id="test_template">
  <style>.page { color: black; }</style>
  <components><sceneHeading class="scene-heading"/></components>
  <content><sceneHeading>INT. ROOM - DAY</sceneHeading></content>
</template>
"""

def test_init_xml_with_invalid_xml():
    """
    Tests that __init_xml raises a ValueError with malformed XML.
    """
    script = Script(MagicMock(), MagicMock())
    invalid_xml = "<root><unclosed-tag></root>"
    with pytest.raises(ValueError, match="Invalid XML format"):
        script._Script__init_xml(invalid_xml)

def test_create_script_db_failure():
    """
    Tests that create raises an exception if the database call fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    mock_db.add_script.side_effect = Exception("DB connection failed")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="DB connection failed"):
        script.create(mock_template, "Test Title", uuid.uuid4(), uuid.uuid4())
    
    mock_storage.put.assert_not_called()

def test_create_script_storage_failure_and_rollback():
    """
    Tests that create raises an exception if storage fails, and that the DB entry is rolled back.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    mock_script_obj = MagicMock()

    mock_db.add_script.return_value = mock_script_obj
    mock_storage.put.side_effect = Exception("S3 bucket not found")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="S3 bucket not found"):
        script.create(mock_template, "Test Title", uuid.uuid4(), uuid.uuid4())

    # Assert that the rollback function was called
    mock_db.delete_script.assert_called_once_with(mock_script_obj)

def test_open_script_not_found_in_db():
    """
    Tests that open raises FileNotFoundError if the script is not in the database.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.open("Nonexistent Script", uuid.uuid4(), uuid.uuid4())

def test_open_script_storage_get_failure():
    """
    Tests that open raises an exception if fetching from storage fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()

    mock_db.get_script.return_value = True
    mock_storage.get.side_effect = Exception("Cloudflare R2 is down")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="Cloudflare R2 is down"):
        script.open("Test Script", uuid.uuid4(), uuid.uuid4())

def test_save_script_not_found_in_db():
    """
    Tests that save raises FileNotFoundError if the script doesn't exist in the DB.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.save("Nonexistent Script", uuid.uuid4(), uuid.uuid4(), [])

def test_save_script_storage_put_failure():
    """
    Tests that save raises an exception if the storage put call fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()
    title = "My Script"

    # Mock successful open
    mock_db.get_script.return_value = True
    mock_storage.get.return_value = {'Body': MagicMock(read=lambda: mock_template.encode('utf-8'))}
    # Mock failed save
    mock_storage.put.side_effect = Exception("Failed to write to bucket")

    script = Script(mock_storage, mock_db)
    script.open(title, userid, projectid) # Load initial state

    with pytest.raises(Exception, match="Failed to write to bucket"):
        script.save(title, userid, projectid, [{'class': 'scene-heading', 'content': 'NEW CONTENT'}])

def test_save_script_invalid_json_content():
    """
    Tests that save raises a ValueError if the new content has a class not in the tag_map.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()
    title = "My Script"

    mock_db.get_script.return_value = True
    mock_storage.get.return_value = {'Body': MagicMock(read=lambda: mock_template.encode('utf-8'))}

    script = Script(mock_storage, mock_db)
    script.open(title, userid, projectid)

    invalid_content = [{'class': 'non-existent-class', 'content': 'This will fail'}]

    with pytest.raises(ValueError, match="No tag found for class: non-existent-class"):
        script.save(title, userid, projectid, invalid_content)

def test_delete_script_not_found_in_db():
    """
    Tests that delete raises FileNotFoundError if the script is not in the database.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.delete("Nonexistent Script", uuid.uuid4(), uuid.uuid4())

def test_delete_script_storage_failure():
    """
    Tests that delete raises an exception if the storage call fails.
    The database entry should NOT be deleted in this case.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()

    mock_db.get_script.return_value = True
    mock_storage.delete.side_effect = Exception("Storage delete failed")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="Storage delete failed"):
        script.delete("Test Script", uuid.uuid4(), uuid.uuid4())

    mock_db.delete_script.assert_not_called()

def test_delete_project_storage_failure():
    """
    Tests that delete_project raises an exception if a storage deletion fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()

    script1 = MagicMock(title="Script1")
    mock_db.get_list_of_scripts.return_value = [script1]
    mock_storage.delete.side_effect = Exception("Partial storage failure")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="Partial storage failure"):
        script.delete_project(userid, projectid)

    # Ensure it attempted the deletion
    mock_storage.delete.assert_called_once_with(f"users/{userid}/projects/{projectid}/scripts/Script1.lss")
    # Ensure the DB was not touched because storage failed
    mock_db.delete_script.assert_not_called()
