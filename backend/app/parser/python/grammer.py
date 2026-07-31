from tree_sitter import Language
from tree_sitter_language_pack import get_language


class PythonGrammar:

    _language = None

    @classmethod
    def language(cls):

        if cls._language is None:

            cls._language = get_language("python")

        return cls._language