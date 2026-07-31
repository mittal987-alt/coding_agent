from tree_sitter import Node

from app.schemas.parser import (
    FunctionSymbol,
    ClassSymbol,
)


class SymbolExtractor:

    def extract(
        self,
        root: Node,
        source: bytes,
    ):

        functions = []
        classes = []

        self._walk(
            root,
            source,
            functions,
            classes,
            current_class=None,
        )

        return {

            "functions": functions,

            "classes": classes,
        }


class SymbolExtractor:

    def extract(
        self,
        root: Node,
        source: bytes,
    ):

        functions = []
        classes = []

        self._walk(
            root,
            source,
            functions,
            classes,
            current_class=None,
        )

        return {

            "functions": functions,

            "classes": classes,
        }


  def _walk(
    self,
    node,
    source,
    functions,
    classes,
    current_class,
):

    if node.type == "class_definition":

        cls = self._extract_class(
            node,
            source,
        )

        classes.append(cls)

        current_class = cls.name

    elif node.type == "function_definition":

        fn = self._extract_function(
            node,
            source,
            current_class,
        )

        functions.append(fn)

        if current_class:

            for cls in classes:

                if cls.name == current_class:
                    cls.methods.append(fn.name)

    for child in node.children:

        self._walk(
            child,
            source,
            functions,
            classes,
            current_class,
        )

    def _extract_class(
    self,
    node,
    source,
):

    identifier = None

    for child in node.children:

        if child.type == "identifier":

            identifier = source[
                child.start_byte:
                child.end_byte
            ].decode()

            break

    return ClassSymbol(

        name=identifier,

        methods=[],

        start_line=node.start_point[0] + 1,

        end_line=node.end_point[0] + 1,
    )
  

  def _extract_function(
    self,
    node,
    source,
    class_name,
):

    name = ""

    parameters = []

    for child in node.children:

        if child.type == "identifier":

            name = source[
                child.start_byte:
                child.end_byte
            ].decode()

        if child.type == "parameters":

            for p in child.children:

                if p.type == "identifier":

                    parameters.append(

                        source[
                            p.start_byte:
                            p.end_byte
                        ].decode()
                    )

    return FunctionSymbol(

        name=name,

        class_name=class_name,

        parameters=parameters,

        start_line=node.start_point[0] + 1,

        end_line=node.end_point[0] + 1,
    )

    parser = ParserManager()

parsed = parser.parse_file(
    Path("main.py")
)

extractor = SymbolExtractor()

symbols = extractor.extract(
    parsed["tree"].root_node,
    parsed["source"],
)

print(symbols)