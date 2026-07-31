class DocumentationRetriever:

    async def retrieve(

        self,

        provider,

        query,

    ):

        return await provider.search(

            query

        )