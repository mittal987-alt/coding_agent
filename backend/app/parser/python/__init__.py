from app.parser.base.registry import ParserRegistry

from .parser import PythonParser

ParserRegistry.register(

    "python",

    PythonParser(),

)