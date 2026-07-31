class ResultRanker:

    def rank(

        self,

        results,

    ):

        priority = [

            "docs.",

            "developer.",

            "github.com",

            "stackoverflow.com",

        ]

        return sorted(

            results,

            key=lambda r: any(

                p in r.url

                for p in priority

            ),

            reverse=True,

        )