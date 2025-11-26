from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def put():
        pass
    @abstractmethod
    def get():
        pass
    @abstractmethod
    def update():
        pass
    @abstractmethod
    def delete():
        pass
    @abstractmethod
    def delete_many():
        pass
    @abstractmethod
    def list_files():
        pass

