from app.parser.base.base_parser import BaseParser


class ParserRegistry:

    _registry = {}

    @classmethod
    def register(

        cls,

        language: str,

        parser: BaseParser,

    ):

        cls._registry[language] = parser

    @classmethod
    def get(

        cls,

        language: str,

    ) -> BaseParser:

        parser = cls._registry.get(language)

        if parser is None:

            raise ValueError(

                f"No parser for {language}"

            )

        return parser

    @classmethod
    def languages(cls):

        return list(cls._registry.keys())