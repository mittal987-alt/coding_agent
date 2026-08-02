import os
import httpx
import json
import math

async def get_embedding(text: str) -> list[float]:
    """
    Calls the Gemini API to get the text embedding for the given string.
    Returns a list of floats representing the vector.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found. Returning empty embedding.")
        return []

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{"text": text}]
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                return result["embedding"]["values"]
            else:
                print(f"Error fetching embedding: {response.status_code} {response.text}")
                return []
    except Exception as e:
        print(f"Exception fetching embedding: {e}")
        return []

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Computes the cosine similarity between two vectors.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)
