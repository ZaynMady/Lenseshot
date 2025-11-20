from abc import ABC, abstractmethod

class File(ABC):
    # Abstract base class for file operations

    #CRUD Operations

    @abstractmethod
    def create(content, storage):
        
        pass