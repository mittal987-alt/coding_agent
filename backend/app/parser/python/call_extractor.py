class CallExtractor:

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

    calls = []

    captures = self.query.captures(root)

    for node, capture in captures:

        calls.append(

            source[
                node.start_byte:
                node.end_byte
            ].decode()

        )

    return calls