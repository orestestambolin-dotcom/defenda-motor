from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_text import extract_text_from_pdf_bytes
from app.services.llm import analyze_legal_text

router = APIRouter()

@router.post("/upload/analyze")
async def upload_and_analyze(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    try:
        text = extract_text_from_pdf_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao ler PDF: {str(e)}")

    # guarda-raio: evita mandar livro inteiro para IA
    if len(text) < 200:
        raise HTTPException(status_code=400, detail="Texto muito curto. PDF pode estar como imagem/scaneado.")

    result = await analyze_legal_text(text[:80_000])  # MVP: corta para não explodir tokens
    return {
        "filename": file.filename,
        "chars_extracted": len(text),
        "analysis": result
    }
