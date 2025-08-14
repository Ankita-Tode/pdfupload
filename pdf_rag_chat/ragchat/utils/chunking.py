from typing import List, Dict

def chunk_text(pages, chunk_size=1000, overlap=200):
    """
    pages: iterable[(page_num, text)]
    Returns list of dict chunks with {'id','text','page_start','page_end'}
    """
    chunks: List[Dict] = []
    buf, buf_pages = [], []

    def flush():
        if not buf:
            return
        text = "".join(buf)
        page_start = buf_pages[0]
        page_end = buf_pages[-1]
        chunks.append({
            "id": f"{page_start}-{page_end}-{len(chunks)}",
            "text": text,
            "page_start": page_start,
            "page_end": page_end
        })

    for page_num, text in pages:
        if not text:
            continue
        i = 0
        while i < len(text):
            # remaining space in current buffer
            remaining = chunk_size - sum(len(x) for x in buf)
            if remaining <= 0:
                flush()
                # keep tail for overlap
                tail = "".join(buf)[-overlap:] if overlap > 0 else ""
                buf = [tail] if tail else []
                buf_pages = [buf_pages[-1]] if buf_pages else []
                continue
            take = text[i:i+remaining]
            buf.append(take)
            if not buf_pages or buf_pages[-1] != page_num:
                buf_pages.append(page_num)
            i += len(take)
        # ensure flushing when crossing large pages
        if sum(len(x) for x in buf) >= chunk_size:
            flush()
            tail = "".join(buf)[-overlap:] if overlap > 0 else ""
            buf = [tail] if tail else []
            buf_pages = [page_num] if tail else []

    flush()
    return chunks
