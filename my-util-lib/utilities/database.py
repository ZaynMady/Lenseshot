from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from abc import ABC, abstractmethod

class Database:
    def __init__(self, database_url=None, with_engine=None):
        self.__db = SQLAlchemy()
        if not with_engine:
            self.__engine = create_engine(database_url, pool_pre_ping=True)
        else:
            self.__engine = with_engine
        self._Session = sessionmaker(bind=self.__engine)
        self._session = self._Session()
    
    #initializing flask app with db
    def app(self, flask_app):
        self.__db.init_app(flask_app)
    
    @property
    def engine(self):
        return self.__engine

    def rollback(self):
        self._session.rollback()

