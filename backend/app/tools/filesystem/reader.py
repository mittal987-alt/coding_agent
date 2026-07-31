from pathlib import Path


class FileReader:

    def read(

        self,

        path: Path,

    ) -> str:

        return path.read_text(

            encoding="utf-8"

        )

    def read_lines(

        self,

        path: Path,

        start: int,

        end: int,

    ):

        lines = path.read_text().splitlines()

        return "\n".join(

            lines[start:end]

        )