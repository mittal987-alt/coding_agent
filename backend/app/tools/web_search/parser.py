from bs4 import BeautifulSoup


class DocumentationParser:

    def parse(

        self,

        html: str,

    ):

        soup = BeautifulSoup(

            html,

            "html.parser",

        )

        return soup.get_text(
            "\n",
            strip=True,
        )