from abc import ABC, abstractmethod

class File(ABC):
    def __init__(self, content, path, **kwargs):
        self.content = content
        self.path = path
    
    @abstractmethod
    def create():
        pass
    @abstractmethod
    def save():
        pass
    @abstractmethod
    def delete():
        pass
    @abstractmethod
    def update():
        pass