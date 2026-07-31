from pathlib import Path

BASE_STORAGE = Path("storage")

PROJECT_STORAGE = BASE_STORAGE / "projects"

PROJECT_STORAGE.mkdir(
    parents=True,
    exist_ok=True
)