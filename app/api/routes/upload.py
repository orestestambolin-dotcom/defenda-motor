from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_text import extract_text_from_pdf_bytes

router = APIRouter(prefix="/v1/upload", tags=["Upload"])

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Arquivo deve ser PDF")

    try:
        pdf_bytes = await file.read()

        text, pages = extract_text_from_pdf_bytes(pdf_bytes)

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Não foi possível extrair texto do PDF"
            )

        return {
            "success": True,
            "pages": pages,
            "text_length": len(text),
            "preview": text[:1000],  # preview para debug
            "text": text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDF: {str(e)}"
        )
