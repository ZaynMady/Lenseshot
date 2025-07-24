from . import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)

class Project_members(db.Model):
    __tablename__ = 'project_members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=True)  # e.g., 'admin', 'editor', 'viewer'
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
