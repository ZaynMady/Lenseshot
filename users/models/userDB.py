from utilities.database import Database
from .userModel import UserModel, Contacts
from datetime import datetime, timezone
import uuid
from sqlalchemy.exc import IntegrityError

class UserDB(Database):
    def __init__(self, database_url=None, with_engine=None):
        if not with_engine:
            super().__init__(database_url)
        else: #we are in testing mode, use the provided enging
            super().__init__(with_engine=with_engine)
    
    #Basic CRUD operations for UserModel
    def add_user(self, username, email, auth_id, role=None, profile_picture=None, bio=None, rate=None):
        try:
            new_user = UserModel(
                id=uuid.uuid4(),
                username=username,
                email=email,
                Auth=auth_id,
                role=role,
                profile_picture=profile_picture,
                bio=bio,
                created_at=datetime.now(timezone.utc),
                rate=rate
            )
            self._session.add(new_user)
            # MUST commit (or flush) to trigger the database constraint check
            self._session.commit() 
            return new_user

        except IntegrityError as ie:
            self._session.rollback()
            # Note: Using .orig is correct for getting the database-specific error
            if 'UNIQUE constraint failed' in str(ie.orig):
                raise Exception("User with this username or email already exists.")
            else:
                raise ie
    
    def get_user(self, username):
        return self._session.query(UserModel).filter_by(username=username).first()
    
    def update_user_data(self, user, **kwargs):
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self._session.commit()

    def delete_user(self, user):
        self._session.delete(user)
        self._session.commit()

    #adding and managing contacts
    def add_contact(self, user_id, contact_id):
        new_contact = Contacts(
            id=uuid.uuid4(),
            user_id=user_id,
            contact_id=contact_id
        )
        self._session.add(new_contact)
        self._session.commit()
        return new_contact
    
    def get_contacts(self, user_id):
        return self._session.query(Contacts).filter_by(user_id=user_id).all()
    
    def delete_contact(self, contact):
        self._session.delete(contact)
        self._session.commit()
