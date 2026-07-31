from tree_sitter import Query


class ImportExtractor:

    def __init__(
        self,
        language,
        query,
    ):

        self.query = Query(
            language,
            query,
        )

    def extract(
        self,
        root,
        source,
    ):

        imports = []

        captures = self.query.captures(root)

        for node, capture in captures:

            text = source[
                node.start_byte:
                node.end_byte
            ].decode()

            imports.append(text)

        return imports