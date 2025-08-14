import fitz  # PyMuPDF

def extract_pages_text(pdf_path: str):
    """
    Generator yielding (page_number, text) for each page.
    Uses memory-mapped access, efficient for 500+ pages.
    """
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text")
            yield i, (text or "").strip()
