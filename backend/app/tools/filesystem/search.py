from pathlib import Path

from .models import FileSearchResult


class FileSearcher:

    def search(

        self,

        root: Path,

        query: str,

    ):

        results = []

        for file in root.rglob("*"):

            if not file.is_file():

                continue

            try:

                for number, line in enumerate(

                    file.read_text(

                        errors="ignore"

                    ).splitlines(),

                    start=1,

                ):

                    if query in line:

                        results.append(

                            FileSearchResult(

                                path=str(file),

                                line=number,

                                content=line,

                            )

                        )

            except Exception:

                continue

        return results