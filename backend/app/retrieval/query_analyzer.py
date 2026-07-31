from enum import Enum
import re


class QueryIntent(str, Enum):

    EXPLAIN = "explain"

    FIND_SYMBOL = "find_symbol"

    FIND_REFERENCE = "find_reference"

    IMPLEMENT = "implement"

    DEBUG = "debug"

    TEST = "test"

    REFACTOR = "refactor"

    UNKNOWN = "unknown"

  

class QueryAnalyzer:

    def analyze(
        self,
        query: str,
    ) -> QueryIntent:

        q = query.lower()

        if re.search(r"where.*defined", q):
            return QueryIntent.FIND_SYMBOL

        if "definition" in q:
            return QueryIntent.FIND_SYMBOL

        if "reference" in q:
            return QueryIntent.FIND_REFERENCE

        if "how does" in q:
            return QueryIntent.EXPLAIN

        if "implement" in q:
            return QueryIntent.IMPLEMENT

        if "bug" in q:
            return QueryIntent.DEBUG

        if "test" in q:
            return QueryIntent.TEST

        return QueryIntent.UNKNOWN