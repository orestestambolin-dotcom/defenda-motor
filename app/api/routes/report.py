from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services.pdf_text import extract_text_from_pdf_bytes
from app.services.llm import analyze_legal_text
from app.services.pdf_report import build_legal_report_pdf

router = APIRouter()

@router.post("/report/pdf")
async def generate_pdf_report(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    data = await file.read()
    text = extract_text_from_pdf_bytes(data)
    if len(text) < 200:
        raise HTTPException(status_code=400, detail="Texto muito curto. PDF pode estar escaneado/imagem.")

    analysis = await analyze_legal_text(text[:80_000])
    if isinstance(analysis, dict) and analysis.get("error"):
        raise HTTPException(status_code=500, detail=analysis["error"])

    pdf_bytes = build_legal_report_pdf(
        filename=file.filename,
        analysis=analysis,
        case_title="Relatório de Triagem — Execução Bancária / CCB / Monitória"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="relatorio_{file.filename}.pdf"'}
    )
