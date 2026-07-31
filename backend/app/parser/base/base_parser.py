from abc import ABC
from abc import abstractmethod

from pathlib import Path

from app.parser.base.symbol import Symbol


class BaseParser(ABC):

    @abstractmethod
    def parse(
        self,
        file: Path,
    ) -> list[Symbol]:

        """
        Parse source file.

        Return symbols.
        """

        pass