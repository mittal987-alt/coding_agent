from pathlib import Path


class FileWriter:

    def write(

        self,

        path: Path,

        content: str,

    ):

        path.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        path.write_text(

            content,

            encoding="utf-8",

        )

    def append(

        self,

        path: Path,

        content: str,

    ):

        with open(

            path,

            "a",

            encoding="utf-8",

        ) as f:

            f.write(content)