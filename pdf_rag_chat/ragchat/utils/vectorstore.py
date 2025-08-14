import os, json
from pathlib import Path
import numpy as np
import faiss

class VectorStore:
    def __init__(self, index_path: str, meta_path: str, dim: int):
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.dim = dim
        self.index = None
        self.meta = []

    def build(self, embeddings: np.ndarray, meta_list):
        assert embeddings.shape[1] == self.dim
        self.index = faiss.IndexFlatIP(self.dim)
        self.meta = meta_list
        self.index.add(embeddings)

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            for m in self.meta:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")

    def load(self):
        self.index = faiss.read_index(str(self.index_path))
        self.meta = []
        with open(self.meta_path, "r", encoding="utf-8") as f:
            for line in f:
                self.meta.append(json.loads(line))
        return self

    def search(self, query_vec: np.ndarray, top_k: int = 5):
        # query_vec: (1, dim) normalized
        D, I = self.index.search(query_vec, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            m = self.meta[idx]
            m["score"] = float(score)
            results.append(m)
        return results
