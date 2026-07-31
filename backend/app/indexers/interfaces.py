from abc import ABC
from abc import abstractmethod


class ScannerInterface(ABC):

    @abstractmethod
    def scan(self, path):
        ...


class ParserInterface(ABC):

    @abstractmethod
    def parse(self, file):
        ...


class EmbeddingInterface(ABC):

    @abstractmethod
    def build(self, chunks):
        ...