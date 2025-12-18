#FILE FOR TESTING DATABASE INTEGRATION 
from users.models.userDB import UserDB
from users.models.userModel import Base
from sqlalchemy import create_engine
import uuid

import pytest
import csv
from uuid import UUID

@pytest.fixture
def user_db():
    # 1. Create the engine ONCE
    engine = create_engine("sqlite:///:memory:")
    
    # 2. Use the metadata from the Base to create tables on THAT engine
    Base.metadata.create_all(engine)
    
    # 3. Pass that specific engine to your UserDB
    # (Note: This assumes your UserDB class can accept an engine object)
    return UserDB(with_engine=engine)


def get_test_data():
    """Helper to parse CSV safely with proper data types."""
    rows = []
    with open("users/tests/users.csv", "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert strings to the types your UserModel expects
            row['Auth'] = UUID(row['Auth'])
            row['rate'] = float(row['rate']) if row['rate'] else 0.0
            rows.append(row)
    return rows

#CRUD TESTING
@pytest.mark.parametrize("data", get_test_data())
def test_add_user(user_db, data):
    # Pass data as a dictionary or unpacked kwargs
    new_user = user_db.add_user(
        username=data['username'], 
        email=data['email'], 
        auth_id=data['Auth'], 
        role=data['role'], 
        profile_picture=data['profile_picture'], 
        bio=data['bio'], 
        rate=data['rate']
    )
    
    assert new_user.username == data['username']
    assert str(new_user.Auth) == str(data['Auth'])
    assert float(new_user.rate) == data['rate']
    assert new_user.email == data['email']

@pytest.mark.parametrize("data", get_test_data())
def test_get_user(user_db, data):
    new_user = user_db.add_user(
        username=data['username'], 
        email=data['email'], 
        auth_id=data['Auth'], 
        role=data['role'], 
        profile_picture=data['profile_picture'], 
        bio=data['bio'], 
        rate=data['rate']
    )
    
    retrieved_user = user_db.get_user(data['username'])
    
    assert retrieved_user.username == data['username']
    assert str(retrieved_user.Auth) == str(data['Auth'])
    assert float(retrieved_user.rate) == data['rate']
    assert retrieved_user.email == data['email']

@pytest.mark.parametrize("data", get_test_data())
def test_update_user_data(user_db, data):
    new_user = user_db.add_user(
        username=data['username'], 
        email=data['email'], 
        auth_id=data['Auth'], 
        role=data['role'], 
        profile_picture=data['profile_picture'], 
        bio=data['bio'], 
        rate=data['rate']
    )

    updated_bio = "Updated bio for testing."
    user_db.update_user_data(new_user, bio=updated_bio)

    retrieved_user = user_db.get_user(data['username'])
    
    assert retrieved_user.bio == updated_bio

@pytest.mark.parametrize("data", get_test_data())
def test_delete_user(user_db, data):
    new_user = user_db.add_user(
        username=data['username'], 
        email=data['email'], 
        auth_id=data['Auth'], 
        role=data['role'], 
        profile_picture=data['profile_picture'], 
        bio=data['bio'], 
        rate=data['rate']
    )

    user_db.delete_user(new_user)

    retrieved_user = user_db.get_user(data['username'])
    
    assert retrieved_user is None

#CONTACT TESTING
@pytest.mark.parametrize("data", get_test_data())
def test_add_contact(user_db, data):
    # First, add two users
    user1 = user_db.add_user(
        username=data['username'], 
        email=data['email'], 
        auth_id=data['Auth'], 
        role=data['role'], 
        profile_picture=data['profile_picture'], 
        bio=data['bio'], 
        rate=data['rate']
    )
    contact_data = {
        'username': data['username'] + "_contact",
        'email': "contact_" + data['email'],
        'auth_id': uuid.uuid4(),  # <--- Change 'Auth' to 'auth_id'
        'role': data['role'],
        'profile_picture': data['profile_picture'],
        'bio': data['bio'],
        'rate': data['rate']
    }
    user2 = user_db.add_user(**contact_data)

    new_contact = user_db.add_contact(user1.id, user2.id)

    assert new_contact.user_id == user1.id
    assert new_contact.contact_id == user2.id

@pytest.mark.parametrize("data", get_test_data())
def test_get_contacts(user_db, data):
    # First, add two users
    user1 = user_db.add_user(
        username=data['username'],
        email=data['email'],
        auth_id=data['Auth'],
        role=data['role'],
        profile_picture=data['profile_picture'],
        bio=data['bio'],
        rate=data['rate']
    )
    # Inside test_add_contact, test_get_contacts, and test_delete_contact:

    contact_data = {
        'username': data['username'] + "_contact",
        'email': "contact_" + data['email'],
        'auth_id': uuid.uuid4(),  # <--- Change 'Auth' to 'auth_id'
        'role': data['role'],
        'profile_picture': data['profile_picture'],
        'bio': data['bio'],
        'rate': data['rate']
    }
    user2 = user_db.add_user(**contact_data)

    user_db.add_contact(user1.id, user2.id)

    contacts = user_db.get_contacts(user1.id)

    assert len(contacts) == 1
    assert contacts[0].contact_id == user2.id

@pytest.mark.parametrize("data", get_test_data())
def test_delete_contact(user_db, data):
    # First, add two users
    user1 = user_db.add_user(
        username=data['username'],
        email=data['email'],
        auth_id=data['Auth'],
        role=data['role'],
        profile_picture=data['profile_picture'],
        bio=data['bio'],
        rate=data['rate']
    )
    contact_data = {
        'username': data['username'] + "_contact",
        'email': "contact_" + data['email'],
        'auth_id': uuid.uuid4(),  # <--- Change 'Auth' to 'auth_id'
        'role': data['role'],
        'profile_picture': data['profile_picture'],
        'bio': data['bio'],
        'rate': data['rate']
    }
    user2 = user_db.add_user(**contact_data)

    new_contact = user_db.add_contact(user1.id, user2.id)

    user_db.delete_contact(new_contact)

    contacts = user_db.get_contacts(user1.id)

    assert len(contacts) == 0

# Failure tests

@pytest.mark.parametrize("data", get_test_data())
def test_add_duplicate_user(user_db, data):
    user_db.add_user(
        username=data['username'],
        email=data['email'],
        auth_id=data['Auth'],
        role=data['role'],
        profile_picture=data['profile_picture'],
        bio=data['bio'],
        rate=data['rate']
    )

    # Use 'as exc_info' to capture the exception context
    with pytest.raises(Exception) as exc_info:
        user_db.add_user(
            username=data['username'],
            email=data['email'],
            auth_id=data['Auth'],
            role=data['role'],
            profile_picture=data['profile_picture'],
            bio=data['bio'],
            rate=data['rate']
        )

    # Access the exception message via exc_info.value
    assert "User with this username or email already exists." in str(exc_info.value)