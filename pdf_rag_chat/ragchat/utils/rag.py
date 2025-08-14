import os
import numpy as np
from .embeddings import embed_texts, EMBED_DIM_BY_MODEL
from .vectorstore import VectorStore
from .pdf import extract_pages_text
from .chunking import chunk_text

def build_index(pdf_path: str, faiss_dir: str, embed_model: str, chunk_size: int, overlap: int):
    # 1) Extract text per page
    pages = list(extract_pages_text(pdf_path))

    # 2) Chunk
    chunks = chunk_text(pages, chunk_size=chunk_size, overlap=overlap)
    texts = [c["text"] for c in chunks]

    # 3) Embed
    embs = embed_texts(texts, model=embed_model)
    dim = embs.shape[1]

    # 4) Persist FAISS + JSONL
    index_path = os.path.join(faiss_dir, "index.faiss")
    meta_path = os.path.join(faiss_dir, "chunks.jsonl")
    vs = VectorStore(index_path, meta_path, dim)
    vs.build(embs, chunks)
    vs.save()

    return index_path, meta_path, len(pages), len(chunks)

def load_store(faiss_dir: str, embed_model: str):
    dim = EMBED_DIM_BY_MODEL.get(embed_model, 3072)
    index_path = os.path.join(faiss_dir, "index.faiss")
    meta_path = os.path.join(faiss_dir, "chunks.jsonl")
    vs = VectorStore(index_path, meta_path, dim).load()
    return vs

def retrieve(vs: VectorStore, question: str, embed_model: str, top_k: int = 5):
    qvec = embed_texts([question], model=embed_model)  # normalized
    return vs.search(qvec, top_k=top_k)

def assemble_prompt(system_prompt: str, question: str, contexts, max_tokens: int):
    # Concatenate top chunks, clipped to a rough token budget by length
    context_texts = []
    current = 0
    for c in contexts:
        t = c["text"].strip()
        if not t:
            continue
        length = len(t)
        if current + length > max_tokens * 4:  # rough char≃tokens*4
            break
        context_texts.append(f"[pages {c['page_start']+1}-{c['page_end']+1}] {t}")
        current += length

    context_block = "\n\n---\n\n".join(context_texts) or "No relevant context found."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content":
            f"Answer the question using ONLY the context below.\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {question}"
        },
    ]
    return messages, context_block

