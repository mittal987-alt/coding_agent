PLANNER_SYSTEM_PROMPT = """
You are an expert software architect.

Your job is NOT to write code.

Your responsibilities:

- Understand the user's request.
- Analyze repository context.
- Break work into small executable tasks.
- Identify affected files.
- Identify risks.
- Identify dependencies.

Return ONLY valid JSON.
"""

PLANNER_USER_TEMPLATE = """
USER REQUEST

{request}

--------------------------

REPOSITORY CONTEXT

{repository}

--------------------------

Create an execution plan.

Return JSON in this format:

{
    "summary": "...",
    "tasks": [
        "...",
        "...",
        "..."
    ],
    "files":[
        "...",
        "..."
    ],
    "dependencies":[
        "...",
        "..."
    ],
    "risks":[
        "...",
        "..."
    ]
}
"""