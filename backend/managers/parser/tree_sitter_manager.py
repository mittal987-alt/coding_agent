from pathlib import Path

from tree_sitter import Parser
from tree_sitter_language_pack import get_language


class TreeSitterManager:

    def __init__(self):

        self.parsers = {}

    def get_parser(self, language: str):

        if language in self.parsers:
            return self.parsers[language]

        parser = Parser()

        parser.set_language(
            get_language(language)
        )

        self.parsers[language] = parser

        return parser

    def parse(
        self,
        file_path: Path,
        language: str,
    ):

        parser = self.get_parser(language)

        code = file_path.read_bytes()

        tree = parser.parse(code)

        return tree, code