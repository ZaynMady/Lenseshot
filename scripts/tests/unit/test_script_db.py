import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.models.ScriptModel import Base, ScriptsModel
from scripts.models.ScriptDB import ScriptDB


@pytest.fixture(scope="function")
def script_db_instance():
    """
    Fixture to provide a ScriptDB instance with an in-memory SQLite database.
    This runs for each test function to ensure a clean state.
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # The ScriptDB class manages its own session, so we pass the URL
    db = ScriptDB(database_url='sqlite:///:memory:')
    # We need to bind our test engine to the session used by the class
    db._session = sessionmaker(bind=engine)()

    yield db

    db._session.close()
    Base.metadata.drop_all(engine)


def test_add_script(script_db_instance):
    """
    Tests that a script can be successfully added to the database.
    """
    owner_id = uuid.uuid4()
    project_id = uuid.uuid4()
    title = "My First Script"

    new_script = script_db_instance.add_script(
        title=title,
        owner_id=owner_id,
        project_id=project_id,
        template="test_template"
    )

    assert isinstance(new_script, ScriptsModel)
    assert new_script.title == title
    assert new_script.owner_id == owner_id

    # Verify it's in the database
    retrieved = script_db_instance._session.query(ScriptsModel).filter_by(id=new_script.id).one()
    assert retrieved is not None


def test_get_script(script_db_instance):
    """
    Tests retrieving a specific script from the database.
    """
    owner_id = uuid.uuid4()
    title = "The Script to Find"
    script_to_add = ScriptsModel(id=uuid.uuid4(), title=title, owner_id=owner_id, templates="default")
    script_db_instance._session.add(script_to_add)
    script_db_instance._session.commit()

    # Test successful retrieval
    found_script = script_db_instance.get_script(script_title=title, owner_id=owner_id)
    assert found_script is not None
    assert found_script.id == script_to_add.id

    # Test unsuccessful retrieval (wrong owner)
    not_found_script = script_db_instance.get_script(script_title=title, owner_id=uuid.uuid4())
    assert not_found_script is None


def test_update_script_title(script_db_instance):
    """
    Tests updating the title of an existing script.
    """
    script_to_add = ScriptsModel(id=uuid.uuid4(), title="Old Title", owner_id=uuid.uuid4(), templates="default")
    script_db_instance._session.add(script_to_add)
    script_db_instance._session.commit()

    new_title = "A Brand New Title"
    script_db_instance.update_script_title(script_to_add, new_title)

    updated_script = script_db_instance._session.query(ScriptsModel).filter_by(id=script_to_add.id).one()
    assert updated_script.title == new_title


def test_delete_script(script_db_instance):
    """
    Tests deleting a script from the database.
    """
    script_to_delete = ScriptsModel(id=uuid.uuid4(), title="To Be Deleted", owner_id=uuid.uuid4(), templates="default")
    script_id = script_to_delete.id
    script_db_instance._session.add(script_to_delete)
    script_db_instance._session.commit()

    script_db_instance.delete_script(script_to_delete)

    count = script_db_instance._session.query(ScriptsModel).filter_by(id=script_id).count()
    assert count == 0


def test_get_list_of_scripts(script_db_instance):
    """
    Tests retrieving all scripts belonging to a specific owner.
    """
    owner_id = uuid.uuid4()
    script_db_instance._session.add_all([
        ScriptsModel(id=uuid.uuid4(), title="Script 1", owner_id=owner_id, templates="default"),
        ScriptsModel(id=uuid.uuid4(), title="Script 2", owner_id=owner_id, templates="default"),
        ScriptsModel(id=uuid.uuid4(), title="Other User's Script", owner_id=uuid.uuid4(), templates="default")
    ])
    script_db_instance._session.commit()

    user_scripts = script_db_instance.get_list_of_scripts(owner_id=owner_id)
    assert len(user_scripts) == 2
    assert "Other User's Script" not in [s.title for s in user_scripts]