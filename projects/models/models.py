import uuid
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, DateTime, Integer, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
import os
import sys

#getting base from scriptsModel
Base = declarative_base()

# ------------------------
# Projects Table
# ------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner = Column(UUID(as_uuid=True), nullable=False)  # store Supabase user UUID here
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)


# ------------------------
# Project Members Table
# ------------------------
class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(UUID(as_uuid=True), nullable=False)  # FK disabled for Supabase auth
    user_id = Column(UUID(as_uuid=True), nullable=False)     # store Supabase user UUID
    role = Column(String(50))                                # 'admin', 'editor', 'viewer'
    joined_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Ensure a user is not added twice to the same project
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
    )
