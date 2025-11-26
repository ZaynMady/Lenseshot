import pytest
from unittest.mock import MagicMock
from xml.etree import ElementTree as ET
from scripts.common.Script import Script
import uuid

#creating a mock template
mock_template = """<?xml version="1.0" encoding="UTF-8"?>

<template id="american_screenplay" version="1.0">
  <style>
    .page {
      color : black;
    }
    </style>

  <components>
    <sceneHeading class="scene-heading"/>
    <actionBlock class="action"/>
  </components>

  <content>
  <sceneHeading>INT. ROOM</sceneHeading>
  <actionBlock> hello world </actionBlock>  
  </content>

  <smartType>
  </smartType>
</template>
"""


#testing the init xml function 
def test_init_xml_success():
    #Mocking database and storage
    storage = MagicMock()
    database = MagicMock()

    raw_xml = """
    <template id="test">
        <style>.page { color: black; }</style>
        <components><sceneHeading class="scene-heading"/></components>
        <content><sceneHeading>INT. ROOM</sceneHeading></content>
    </template>
    """
    script = Script(storage, database)
    script._Script__init_xml(raw_xml)

    assert script.style == ".page { color: black; }"
    assert "scene-heading" in script.components 
    assert script.content[0]['content'] == "INT. ROOM"
    assert script.file_content == raw_xml

#testing the json to xml function
def test_json_to_xml_success():
    """
    Tests the successful conversion of a JSON-like structure to an XML Element.
    """
    tag_map = {
        'sceneHeading': 'scene-heading',
        'action': 'action-description'
    }
    json_data = [
        {'class': 'scene-heading', 'content': 'INT. TEST ROOM - DAY'},
        {'class': 'action-description', 'content': 'A test is being written.'}
    ]

    # The method is static, so we can call it directly on the class
    xml_element = Script._Script__json_to_xml(json_data, tag_map)

    # Convert the resulting element to a string for comparison
    # We'll strip whitespace to make the comparison less brittle
    result_xml_string = "".join(ET.tostring(xml_element, encoding='unicode').split())

    expected_xml_string = """<content><sceneHeading>INT. TEST ROOM - DAY</sceneHeading><action>A test is being written.</action></content>"""
    expected_xml_string = "".join(expected_xml_string.split())

    assert result_xml_string == expected_xml_string
    assert xml_element.tag == 'content'
    assert len(list(xml_element)) == 2

def test_json_to_xml_missing_tag_failure():
    """
    Tests that a ValueError is raised if a class in the JSON data
    does not have a corresponding tag in the tag_map.
    """
    tag_map = {'sceneHeading': 'scene-heading'}
    json_data = [{'class': 'action', 'content': 'This should fail.'}]

    with pytest.raises(ValueError, match="No tag found for class: action"):
        Script._Script__json_to_xml(json_data, tag_map)

#testing create a new screenplay function 
def test_create_new_script_success():
    """
        Tests that the function can successfuly create a screenplay as expected
    """

    mock_storage = MagicMock()
    mock_db = MagicMock()

    script = Script(mock_storage, mock_db)
    userid = MagicMock()
    projectid = MagicMock()

    newscript = script.create(mock_template, "Godfather", userid, projectid)

    assert newscript == True

    #asserting file content is equal to the template being parsed
    assert script.file_content == mock_template

    #asserting file components are complete
    assert script.components == ["scene-heading", "action"]

    #asserting style
    expected_style = """
    .page {
        color : black;
    }
    """
    assert script.style.replace(" ", "").replace("\n", "") == expected_style.replace(" ", "").replace("\n", "")
    
    #asserting smarttypes
    script.smarttypes == {}

def test_open_script_success():
    """
    Tests that a script can be successfully opened and its content parsed.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()
    title = "My Script"

    # Mock the database to confirm the script exists
    mock_db.get_script.return_value = True
    # Mock storage to return the file content
    mock_storage.get.return_value = {'Body': MagicMock(read=lambda: mock_template.encode('utf-8'))}

    script = Script(mock_storage, mock_db)
    script.open(title, userid, projectid)

    # Assert that the script's properties are populated correctly
    assert script.file_content == mock_template
    assert script.components == ["scene-heading", "action"]
    assert len(script.content) == 2
    assert script.content[0]['class'] == 'scene-heading'

    # Verify that the mocks were called correctly
    mock_db.get_script.assert_called_once_with(title, userid, projectid)
    mock_storage.get.assert_called_once_with(f"users/{userid}/projects/{projectid}/scripts/{title}.lss")

def test_quick_save_success():
    """
    Tests that quick_save updates the in-memory content of the script.
    """
    script = Script(MagicMock(), MagicMock())
    new_content = [{'class': 'scene-heading', 'content': 'A NEW SCENE'}]
    
    script.quick_save(new_content)
    
    assert script.content == new_content

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
    mock_storage.get.return_value = {'Body': MagicMock(read=lambda: mock_template.encode('utf-8'))}

    script = Script(mock_storage, mock_db)
    # Initialize the script by "opening" it first
    script.open(title, userid, projectid)

    # New content to save
    new_content = [
        {'class': 'scene-heading', 'content': 'INT. OFFICE - NIGHT'},
        {'class': 'action', 'content': 'The test passes.'}
    ]

    result = script.save(title, userid, projectid, new_content)

    assert result is True
    # Check that storage.put was called
    mock_storage.put.assert_called_once()
    
    # Get the XML content that was passed to storage.put
    saved_xml = mock_storage.put.call_args[0][1]

    # Verify the new content is in the saved XML
    assert 'INT. OFFICE - NIGHT' in saved_xml
    assert 'The test passes.' in saved_xml
    # Verify that other parts of the template are preserved
    assert '<style>' in saved_xml
    assert '<components>' in saved_xml

def test_delete_script_success():
    """
    Tests that a script is deleted from both storage and the database.
    """
    mock_storage = MagicMock()
    mock_db = MagicMock()
    userid = uuid.uuid4()
    projectid = uuid.uuid4()
    title = "Script to Delete"
    mock_script_obj = MagicMock()

    mock_db.get_script.return_value = mock_script_obj

    script = Script(mock_storage, mock_db)
    result = script.delete(title, userid, projectid)

    assert result is True
    mock_storage.delete.assert_called_once_with(f"users/{userid}/projects/{projectid}/scripts/{title}.lss")
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
    # Check that delete was called for each script
    assert mock_storage.delete.call_count == 2
    assert mock_db.delete_script.call_count == 2
    mock_storage.delete.assert_any_call(f"users/{userid}/projects/{projectid}/scripts/Script1.lss")
    mock_storage.delete.assert_any_call(f"users/{userid}/projects/{projectid}/scripts/Script2.lss")
    mock_db.delete_script.assert_any_call(script1)
    mock_db.delete_script.assert_any_call(script2)