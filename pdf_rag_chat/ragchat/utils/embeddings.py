import os
import numpy as np
from openai import OpenAI
from openai import OpenAI

# Hardcoded API key for quick local test (DON'T use in production)
client = OpenAI(api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

def get_embeddings(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


EMBED_DIM_BY_MODEL = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}

def get_embed_client():
    return OpenAI()

def embed_texts(texts, model=None, batch_size=64):
    model = model or os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
    client = get_embed_client()
    out = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = client.embeddings.create(model=model, input=batch)
        out.extend(e.embedding for e in resp.data)
    arr = np.array(out, dtype="float32")
    # normalize to unit vectors (cosine sim via dot)
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return (arr / norms).astype("float32")