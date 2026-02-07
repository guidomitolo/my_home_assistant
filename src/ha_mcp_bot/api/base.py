from abc import ABC, abstractmethod
from typing import Optional


class BaseClient(ABC):

    @abstractmethod
    def get(self, endpoint: str, params: Optional[dict] = None):
        pass
    
    @abstractmethod
    def post(self, endpoint: str, params:Optional[dict] = None, json_data:Optional[dict] = None):
        pass

    @abstractmethod    
    def close(self):
        pass