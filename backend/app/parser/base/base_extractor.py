from abc import ABC
from abc import abstractmethod

from tree_sitter import Tree

from app.parser.base.symbol import Symbol


class BaseExtractor(ABC):

    @abstractmethod
    def extract(

        self,

        tree: Tree,

        source: bytes,

        file: str,

    ) -> list[Symbol]:

        pass