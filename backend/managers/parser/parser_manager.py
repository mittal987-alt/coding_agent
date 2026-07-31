from pathlib import Path

from app.managers.parser.language_manager import LanguageManager
from app.managers.parser.tree_sitter_manager import TreeSitterManager
from app.parser.base.registry import ParserRegistry

from app.parser.base.language_detector import LanguageDetector


class ParserManager:

    def __init__(self):

        self.tree = TreeSitterManager()

    def parse_file(
        self,
        file_path: Path,
    ):

        language = LanguageManager.detect(file_path)

        if language is None:
            return None

        tree, source = self.tree.parse(
            file_path,
            language,
        )

        return {

            "language": language,

            "tree": tree,

            "source": source,
        }

    
    def parse(

        self,

        file: Path,

    ):

        language = LanguageDetector.detect(file)

        if language is None:

            return []

        parser = ParserRegistry.get(language)

        return parser.parse(file)

        
    def print_tree(node, level=0):

           print(
            "  " * level + node.type
           )

           for child in node.children:
               print_tree(child, level + 1)     


               def print_tree(node, level=0):

                   print(
                    "  " * level + node.type
                   )

               for child in node.children:
                   print_tree(child, level + 1)    