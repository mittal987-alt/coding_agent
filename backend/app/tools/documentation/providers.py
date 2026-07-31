from abc import ABC, abstractmethod


class BaseDocumentationProvider(ABC):

    @abstractmethod
    async def search(

        self,

        query: str,

    ):

        pass