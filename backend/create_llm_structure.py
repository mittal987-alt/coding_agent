import os

base = 'app/llm'
dirs = [
    '',
    'providers',
    'middleware',
    'templates/system',
    'templates/planning',
    'templates/coding',
    'templates/review',
    'templates/debugging'
]

for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)

files = [
    '__init__.py',
    'manager.py',
    'provider.py',
    'registry.py',
    'router.py',
    'prompts.py',
    'tokenizer.py',
    'streaming.py',
    'cache.py',
    'response.py',
    'exceptions.py',
    'providers/__init__.py',
    'providers/openai.py',
    'providers/anthropic.py',
    'providers/ollama.py',
    'providers/mistral.py',
    'providers/gemini.py',
    'providers/openrouter.py',
    'middleware/logging.py',
    'middleware/retry.py',
    'middleware/metrics.py',
    'middleware/guardrails.py',
    'middleware/rate_limit.py'
]

for f in files:
    filepath = os.path.join(base, f)
    with open(filepath, 'w') as fh:
        pass

try:
    os.remove(__file__)
except Exception:
    pass
