from pypdf import PdfReader
import io

def extract_text(pdf_bytes: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = len(reader.pages)
    chunks = []
    for p in reader.pages:
        chunks.append(p.extract_text() or "")
    return "\n\n".join(chunks), pages
    
from pypdf import PdfReader
from io import BytesIO

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()
