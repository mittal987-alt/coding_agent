import os

base_dir = r"c:\projects\coding_assistaant\backend\app\memory"

files = [
    "manager.py",
    "orchestrator.py",
    "retrieval.py",
    "ranking.py",
    "cache.py",
    "models.py",
    "exceptions.py",
    "embeddings.py",
    "lifecycle.py",
    "scheduler.py",
    "analytics.py",
    "episodic/manager.py",
    "episodic/models.py",
    "episodic/repository.py",
    "episodic/retrieval.py",
    "episodic/summarizer.py",
    "semantic/manager.py",
    "semantic/knowledge.py",
    "semantic/ontology.py",
    "semantic/graph.py",
    "vector/manager.py",
    "vector/faiss_store.py",
    "vector/embeddings.py",
    "vector/retrieval.py",
    "vector/ranking.py",
    "decision/manager.py",
    "decision/models.py",
    "decision/repository.py",
    "decision/retrieval.py",
    "conversation/manager.py",
    "conversation/summarizer.py",
    "conversation/history.py",
    "conversation/compression.py",
    "project/manager.py",
    "project/context.py",
    "project/repository.py",
    "learning/manager.py",
    "learning/feedback.py",
    "learning/optimizer.py",
    "learning/evaluator.py",
    "episodic/__init__.py",
    "semantic/__init__.py",
    "vector/__init__.py",
    "decision/__init__.py",
    "conversation/__init__.py",
    "project/__init__.py",
    "learning/__init__.py",
    "__init__.py"
]

for f in files:
    path = os.path.join(base_dir, f)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as file:
        pass

print("Directory structure created successfully.")
