import pytest
from app import create_app, db
from app.models.userbase import user
from flask_bcrypt import Bcrypt

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    bcrypt = Bcrypt(app)
    with app.app_context():
        test_user = user(
            username='testuser',
            email='test@example.com',
            password=bcrypt.generate_password_hash('password123')
        )
        db.session.add(test_user)
        db.session.commit()
        return test_user