from pathlib import Path


class LanguageDetector:

    EXTENSIONS = {

        ".py": "python",

        ".js": "javascript",

        ".jsx": "javascript",

        ".ts": "typescript",

        ".tsx": "typescript",

        ".java": "java",

        ".go": "go",

        ".rs": "rust",

        ".cpp": "cpp",

        ".cc": "cpp",

        ".hpp": "cpp",

        ".dart": "dart",
    }

    @classmethod
    def detect(

        cls,

        file: Path,

    ):

        return cls.EXTENSIONS.get(

            file.suffix.lower()

        )