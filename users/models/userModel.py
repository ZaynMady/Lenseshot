from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = 'users'


    #important details 
    id = Column(UUID(as_uuid=True), primary_key=True)
    Auth = Column(UUID, nullable=False) #references to Auth Service, used for authenticating requests
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)

    #additional details
    role = Column(String, nullable=True) #user role in the application (admin, user, etc.)
    profile_picture = Column(String, nullable=True) #URL to profile picture
    bio = Column(String, nullable=True) #short biography or description
    created_at = Column(DateTime, nullable=False) #account creation timestamp
    rate = Column(Float, nullable=True) #user's hourly rate for projects

class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    # You need these actual Columns to store the UUIDs!
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    contact_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # These are the relationships for easy access in Python
    user = relationship("UserModel", foreign_keys=[user_id])
    contact = relationship("UserModel", foreign_keys=[contact_id])