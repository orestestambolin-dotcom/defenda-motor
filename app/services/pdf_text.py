from pypdf import PdfReader
from io import BytesIO
from typing import Tuple


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Extrai texto de um PDF em bytes.
    Retorna:
      - texto completo
      - número de páginas
    """
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = len(reader.pages)

    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")

    text = "\n\n".join(parts).strip()
    return text, pages
