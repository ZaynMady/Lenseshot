from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ScriptsModel(Base):
    __tablename__ = 'scripts'

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    project_id = Column(UUID(as_uuid=True), nullable=True)
    scenes = relationship("ScenesModel", back_populates="script", cascade="all, delete-orphan")
    templates = Column(String, nullable=False)



class ScenesModel(Base):
    __tablename__ = 'scenes'

    id = Column(UUID(as_uuid=True), primary_key=True)
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.id'), nullable=False)
    scene_number = Column(Integer, nullable=False)
    heading = Column(String, nullable=False)
    location = Column(String, nullable=False)
    time = Column(String, nullable=False)

    script = relationship("ScriptsModel", back_populates="scenes")
