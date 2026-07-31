from tree_sitter import Query
from tree_sitter import Parser

from app.parser.base.symbol import Symbol
from app.parser.base.symbol import SymbolKind

from .queries import (
    FUNCTION_QUERY,
    CLASS_QUERY,
)

class PythonExtractor:

    def __init__(self, language):

        self.language = language

        self.function_query = Query(
            language,
            FUNCTION_QUERY,
        )

        self.class_query = Query(
            language,
            CLASS_QUERY,
        )


    def extract_functions(
    self,
    root,
    source,
    file,
):

    symbols = []

    captures = self.function_query.captures(root)

    for node, capture in captures:

        if capture != "function.name":
            continue

        name = source[
            node.start_byte:
            node.end_byte
        ].decode()

        symbols.append(

            Symbol(

                id=f"{file}:{name}",

                name=name,

                kind=SymbolKind.FUNCTION,

                language="python",

                file=file,

                start_line=node.start_point[0] + 1,

                end_line=node.end_point[0] + 1,
            )
        )

    return symbols


    def extract_classes(
    self,
    root,
    source,
    file,
):

    classes = []

    captures = self.class_query.captures(root)

    for node, capture in captures:

        if capture != "class.name":
            continue

        name = source[
            node.start_byte:
            node.end_byte
        ].decode()

        classes.append(

            Symbol(

                id=f"{file}:{name}",

                name=name,

                kind=SymbolKind.CLASS,

                language="python",

                file=file,

                start_line=node.start_point[0] + 1,

                end_line=node.end_point[0] + 1,
            )
        )

    return classes


    def extract(self, tree, source, file):

        root = tree.root_node

        return self.extract_functions(root, source, file) + \
               self.extract_classes(root, source, file)
    