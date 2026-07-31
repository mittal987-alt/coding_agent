class DocumentationSummarizer:

    async def summarize(

        self,

        llm,

        chunks,

    ):

        prompt = f"""
Summarize the following documentation.

{chunks}
"""

        return await llm.ainvoke(

            prompt

        )