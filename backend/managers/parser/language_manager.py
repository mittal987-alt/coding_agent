from pathlib import Path


class LanguageManager:

    EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
    }

    @classmethod
    def detect(cls, path: Path):

        return cls.EXTENSIONS.get(
            path.suffix.lower()
        )


    
class TreeSitterManager:

    def __init__(self):
        self.parsers = {}

    def parse(
        self,
        file_path: Path,
    ):
        """
        Returns Tree-sitter AST.

        (Implementation added in the next lesson.)
        """
        pass