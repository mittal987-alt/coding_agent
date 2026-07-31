# prompts.py
"""
LLM prompts used by the Task Decomposition Engine.

Guidelines:
- Always return valid JSON.
- Never include markdown.
- Never explain the output.
"""

# ==========================================================
# Goal Parser
# ==========================================================

GOAL_PARSER_PROMPT = """
You are an expert Software Architect.

Your job is to analyze a software request and convert it into a structured JSON object.

Return ONLY valid JSON.

Schema:

{
    "title": "",
    "description": "",
    "project_type": "",
    "language": "",
    "framework": "",
    "requirements": [],
    "constraints": [],
    "metadata": {}
}

Rules:

- Detect the project type.
- Detect the programming language.
- Detect frameworks.
- Detect databases.
- Detect cloud providers.
- Detect deployment platforms.
- Detect AI/ML requirements.
- Detect authentication requirements.
- Detect infrastructure technologies.
- Put unknown technologies inside metadata.
- Never generate text outside JSON.
"""

# ==========================================================
# Task Planner
# ==========================================================

TASK_PLANNER_PROMPT = """
You are a Senior Staff Software Engineer.

Break the project into executable engineering tasks.

Return ONLY JSON.

Each task must follow:

[
  {
    "id": "",
    "title": "",
    "description": "",
    "agent": "",
    "priority": "",
    "estimated_minutes": 15,
    "dependencies": [],
    "metadata": {}
  }
]

Allowed agents:

planner
coder
reviewer
tester
terminal
research
repository
documentation
devops
security

Rules:

- Every task must be atomic.
- Every dependency must reference another task ID.
- Never create circular dependencies.
- Keep dependency chains short.
- Prefer parallel execution whenever possible.
- Create testing tasks.
- Create documentation tasks.
- Create security review tasks.
- Create deployment tasks if applicable.
"""

# ==========================================================
# Dependency Review
# ==========================================================

DEPENDENCY_REVIEW_PROMPT = """
Review the dependency graph.

Return ONLY JSON.

{
    "valid": true,
    "issues": [],
    "recommendations": []
}

Look for:

- Missing dependencies
- Circular dependencies
- Duplicate work
- Sequential tasks that could run in parallel
- Incorrect ordering
"""

# ==========================================================
# Complexity Estimation
# ==========================================================

COMPLEXITY_PROMPT = """
Estimate project complexity.

Return ONLY JSON.

{
    "complexity": "",
    "risk": "",
    "estimated_hours": 0,
    "estimated_tokens": 0,
    "recommended_agents": 1,
    "parallel_execution": true,
    "requires_human_approval": false
}

Complexity values:

TRIVIAL
SIMPLE
MODERATE
COMPLEX
ENTERPRISE
"""

# ==========================================================
# Validation
# ==========================================================

VALIDATION_PROMPT = """
Review the generated execution plan.

Return ONLY JSON.

{
    "valid": true,
    "errors": [],
    "warnings": [],
    "recommendations": []
}

Validate:

- Dependencies
- Missing tasks
- Missing testing
- Missing documentation
- Missing deployment
- Missing security review
"""

# ==========================================================
# Optimization
# ==========================================================

OPTIMIZATION_PROMPT = """
Optimize the execution plan.

Return ONLY JSON.

{
    "parallel_groups": [],
    "critical_path": [],
    "execution_order": [],
    "recommendations": []
}

Optimize for:

- Speed
- Parallel execution
- Reduced token usage
- Balanced agent utilization
- Minimal waiting
"""

# ==========================================================
# Reflection
# ==========================================================

REFLECTION_PROMPT = """
Review the completed task.

Return ONLY JSON.

{
    "success": true,
    "score": 0.95,
    "lessons": [],
    "mistakes": [],
    "recommendations": [],
    "store_in_memory": true
}
"""

# ==========================================================
# Retry Planning
# ==========================================================

RETRY_PROMPT = """
The previous execution failed.

Analyze the failure.

Return ONLY JSON.

{
    "reason": "",
    "retry": true,
    "modified_tasks": [],
    "additional_tasks": [],
    "recommendations": []
}
"""

# ==========================================================
# Human Approval
# ==========================================================

HUMAN_APPROVAL_PROMPT = """
Summarize the execution plan for a human reviewer.

Keep it concise.

Return ONLY JSON.

{
    "summary": "",
    "risks": [],
    "estimated_hours": 0,
    "estimated_cost": 0,
    "approval_required": true
}
"""