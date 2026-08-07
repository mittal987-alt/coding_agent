import logging
import pickle
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".next"}
TEXT_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".css", ".html",
    ".yml", ".yaml", ".toml", ".txt",
}
CHUNK_SIZE = 800    # chars per chunk
CHUNK_OVERLAP = 150
MAX_FILE_SIZE = 500_000


def _chunk_text(text: str, path: str) -> List[Tuple[str, str]]:
    """Returns list of (chunk_text, metadata_label) tuples."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append((chunk, path))
        start = end - CHUNK_OVERLAP
    return chunks


def build_index(repo_path: Path, vectorstore_path: Path) -> int:
    """
    Walk repo_path, chunk text files, embed them, and save a FAISS index +
    metadata to vectorstore_path. Returns number of chunks indexed.
    """
    all_chunks: List[Tuple[str, str]] = []

    for path in repo_path.rglob("*"):
        if path.is_dir() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel_path = str(path.relative_to(repo_path)).replace("\\", "/")
        all_chunks.extend(_chunk_text(content, rel_path))

    if not all_chunks:
        return 0

    model = get_model()
    texts = [c[0] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype(np.float32))

    vectorstore_path.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(vectorstore_path / "index.faiss"))
    with open(vectorstore_path / "chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)

    logger.info("Indexed %d chunks from %s", len(all_chunks), repo_path)
    return len(all_chunks)


def search_index(vectorstore_path: Path, query: str, top_k: int = 5) -> List[Tuple[str, str]]:
    """
    Returns top_k (chunk_text, source_path) tuples most relevant to query.
    Returns [] if no index exists yet.
    """
    index_file = vectorstore_path / "index.faiss"
    chunks_file = vectorstore_path / "chunks.pkl"

    if not index_file.exists() or not chunks_file.exists():
        return []

    try:
        index = faiss.read_index(str(index_file))
        with open(chunks_file, "rb") as f:
            all_chunks = pickle.load(f)
    except Exception as e:
        logger.warning("Failed to load vector index: %s", e)
        return []

    model = get_model()
    query_vec = model.encode([query], convert_to_numpy=True).astype(np.float32)

    k = min(top_k, len(all_chunks))
    if k == 0:
        return []

    distances, idxs = index.search(query_vec, k)
    results = [all_chunks[i] for i in idxs[0] if i < len(all_chunks)]
    return results