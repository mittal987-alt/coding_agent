from abc import ABC, abstractmethod

from .models import SearchRequest
from .models import SearchResponse


class BaseSearchProvider(ABC):

    @abstractmethod
    async def search(

        self,

        request: SearchRequest,

    ) -> SearchResponse:

        pass