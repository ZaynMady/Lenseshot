import pytest
from unittest.mock import MagicMock
from scripts.common.Script import Script
import uuid

# A mock JSON content for use in tests
mock_content = [
    {"class": "scene-heading", "content": "INT. ROOM - DAY"},
    {"class": "action", "content": "A test is run."}
]

def test_create_script_db_failure():
    """
    Tests that create raises an exception if the database call fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    mock_db.add_script.side_effect = Exception("DB connection failed")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="DB connection failed"):
        script.create(mock_content, "Test Title", uuid.uuid4(), uuid.uuid4(), "test_template")
    
    mock_storage.put.assert_not_called()

def test_create_script_storage_failure_rolls_back_db():
    """
    Tests that a storage failure during create causes a database rollback.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    mock_script_obj = MagicMock()
    mock_db.add_script.return_value = mock_script_obj
    mock_storage.put.side_effect = Exception("S3 bucket not found")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="S3 bucket not found"):
        script.create(mock_content, "Test Title", uuid.uuid4(), uuid.uuid4(), "test_template")

    # Assert that the rollback function (delete_script) was called
    mock_db.delete_script.assert_called_once_with(mock_script_obj)

def test_open_script_not_found_in_db():
    """
    Tests that open raises FileNotFoundError if the script is not in the database.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.open("Nonexistent Script", uuid.uuid4())

def test_open_script_storage_get_failure():
    """
    Tests that open raises an exception if the storage get call fails.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()

    mock_db.get_script.return_value = True
    mock_storage.get.side_effect = Exception("Cloudflare R2 is down")

    script = Script(mock_storage, mock_db)
    with pytest.raises(Exception, match="Cloudflare R2 is down"):
        script.open("Test Script", uuid.uuid4())

def test_save_script_not_found_in_db():
    """
    Tests that save raises FileNotFoundError if the script doesn't exist in the DB.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.save("Nonexistent Script", uuid.uuid4(), [])

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
    # Mock failed save
    mock_storage.put.side_effect = Exception("Failed to write to bucket")

    script = Script(mock_storage, mock_db)

    with pytest.raises(Exception, match="Failed to write to bucket"):
        script.save(title, userid, [{'class': 'scene-heading', 'content': 'NEW CONTENT'}])

def test_delete_script_not_found_in_db():
    """
    Tests that delete raises FileNotFoundError if the script is not in the database.
    """
    mock_db = MagicMock()
    mock_db.get_script.return_value = None

    script = Script(MagicMock(), mock_db)
    with pytest.raises(FileNotFoundError, match="Script does not exist in database."):
        script.delete("Nonexistent Script", uuid.uuid4())

import pytest
from unittest.mock import MagicMock
import uuid
from scripts.common.Script import Script 

# A valid XML template for use in tests if needed (can be empty string for this test)
mock_template = ""

def test_delete_script_storage_failure():
    """
    Tests that delete raises an exception if the storage delete call fails.
    """
    # Arrange
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = "test_user_id"
    projectid = "test_project_id"
    script_title = "Script1"

    # Setup the mocks
    # 1. DB must find the script first. We return True so 'if not script_exists' is False.
    #    If this returns None (default), Script.delete raises FileNotFoundError.
    mock_db.get_script.return_value = True 
    
    # 2. Storage is set to fail
    error_message = "Cloudflare R2 is down"
    mock_storage.delete.side_effect = Exception(error_message)

    script = Script(mock_storage, mock_db)

    # Act & Assert
    # Verify that the specific exception propagates up
    with pytest.raises(Exception) as excinfo:
        script.delete(script_title, userid)
    
    # Verify the message matches our storage error
    assert error_message in str(excinfo.value)
    
    # Assert side effects
    # 1. Verify storage delete was attempted with the correct path
    expected_path = f"users/{userid}/scripts/{script_title}.lss"
    mock_storage.delete.assert_called_once_with(expected_path)

    # 2. Ensure the DB delete was NOT called because storage failed first
    mock_db.delete_script.assert_not_called()

# Include other tests from the file if you wiped them out, 
# ensuring they also have correct mocks setup.)
