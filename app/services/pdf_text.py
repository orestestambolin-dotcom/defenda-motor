from pypdf import PdfReader
import io

def extract_text(pdf_bytes: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = len(reader.pages)
    chunks = []
    for p in reader.pages:
        chunks.append(p.extract_text() or "")
    return "\n\n".join(chunks), pages
