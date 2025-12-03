import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.models.ScriptModel import Base, ScriptsModel, ScenesModel


@pytest.fixture(scope="module")
def db_session():
    """
    Fixture to set up an in-memory SQLite database for the test module.
    This provides a clean database for each test module run.
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_script_instance():
    """
    Tests the basic instantiation of a ScriptsModel object.
    """
    script_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    project_id = uuid.uuid4()

    script = ScriptsModel(
        id=script_id,
        title="The Great Test",
        owner_id=owner_id,
        project_id=project_id,
        templates="american_screenplay"
    )

    assert script.id == script_id
    assert script.title == "The Great Test"
    assert script.owner_id == owner_id
    assert script.project_id == project_id
    assert script.templates == "american_screenplay"
    assert script.scenes == []


def test_add_script_to_db(db_session):
    """
    Tests adding a ScriptsModel instance to the database and retrieving it.
    """
    script = ScriptsModel(
        id=uuid.uuid4(),
        title="Database Adventure",
        owner_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        templates="tv_pilot"
    )
    db_session.add(script)
    db_session.commit()

    retrieved_script = db_session.query(ScriptsModel).filter_by(title="Database Adventure").one()
    assert retrieved_script is not None
    assert retrieved_script.id == script.id
    assert retrieved_script.templates == "tv_pilot"


def test_script_scene_relationship(db_session):
    """
    Tests the one-to-many relationship between ScriptsModel and ScenesModel.
    """
    script = ScriptsModel(
        id=uuid.uuid4(),
        title="A Tale of Two Models",
        owner_id=uuid.uuid4(),
        templates="feature_film"
    )
    scene = ScenesModel(
        id=uuid.uuid4(),
        scene_number=1,
        heading="INT. TEST ROOM - DAY",
        location="TEST ROOM",
        time="DAY"
    )
    script.scenes.append(scene)

    db_session.add(script)
    db_session.commit()

    retrieved_script = db_session.query(ScriptsModel).filter_by(title="A Tale of Two Models").one()
    assert len(retrieved_script.scenes) == 1
    assert retrieved_script.scenes[0].heading == "INT. TEST ROOM - DAY"
    assert retrieved_script.scenes[0].script_id == retrieved_script.id

    # Test cascade delete
    script_id_to_check = retrieved_script.id
    db_session.delete(retrieved_script)
    db_session.commit()

    assert db_session.query(ScriptsModel).filter_by(id=script_id_to_check).count() == 0
    assert db_session.query(ScenesModel).filter_by(script_id=script_id_to_check).count() == 0