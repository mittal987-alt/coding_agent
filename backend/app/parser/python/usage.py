from pathlib import Path

import app.parser.python

from app.parser.parser_manager import ParserManager

manager = ParserManager()

symbols = manager.parse(

    Path("main.py")
)

for symbol in symbols:

    print(symbol)