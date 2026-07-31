from pathlib import Path

from tree_sitter import Parser

from app.parser.base.base_parser import BaseParser

from .grammar import PythonGrammar
from .extractor import PythonExtractor

IMPORT_QUERY = """
(import_statement) @import

(import_from_statement) @from_import
"""
class PythonParser(BaseParser):

    def __init__(self):

        self.language = PythonGrammar.language()

        self.parser = Parser()

        self.parser.set_language(
            self.language
        )

        self.extractor = PythonExtractor(
            self.language
        )

    def parse(
        self,
        file: Path,
    ):

        source = file.read_bytes()

        tree = self.parser.parse(source)

        root = tree.root_node

        symbols = []

        symbols.extend(

            self.extractor.extract_functions(

                root,

                source,

                str(file),
            )
        )

        symbols.extend(

            self.extractor.extract_classes(

                root,

                source,

                str(file),
            )
        )

        return symbols