from . import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    producer = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
