from __future__ import annotations

import io
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader

router = APIRouter()

# --- Modelos de resposta (Swagger bonitinho) ---
class ProcessCaseResponse(BaseModel):
    case_id: str
    status: str  # "RECEBIDO" | "PROCESSANDO" | "CONCLUIDO" | "ERRO"


# --- "Banco" provisório em memória (trocar por DB depois) ---
_CASES: Dict[str, Dict[str, Any]] = {}


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extrai texto do PDF (sem OCR). Não faz decode binário."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def _pipeline_process_case(case_id: str, pdf_bytes: bytes) -> None:
    """Processamento assíncrono simples (background task)."""
    try:
        _CASES[case_id]["status"] = "PROCESSANDO"

        text = _extract_text_from_pdf_bytes(pdf_bytes)

        # Aqui você conecta sua IA / regras / timeline, etc.
        # Por enquanto guardo só um resumo e o tamanho do texto.
        _CASES[case_id]["artifacts"] = {
            "text_len": len(text),
            "text_preview": text[:2000],  # cuidado com PDF grande
        }

        _CASES[case_id]["status"] = "CONCLUIDO"
    except Exception as e:
        _CASES[case_id]["status"] = "ERRO"
        _CASES[case_id]["last_error"] = f"{type(e).__name__}: {e}"


@router.post("/v1/cases/process", response_model=ProcessCaseResponse)
async def process_case(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    case_type: str = Form(...),
    title: str = Form(...),
):
    """
    Recebe PDF + metadados e dispara processamento em background.
    Form-data esperado:
      - file: PDF
      - case_type: string
      - title: string
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf")

    content_type = (file.content_type or "").lower()
    # alguns browsers mandam application/octet-stream; então não bloqueio duro,
    # mas aviso pelo tipo se for algo muito diferente:
    if content_type and "pdf" not in content_type and content_type != "application/octet-stream":
        raise HTTPException(status_code=400, detail=f"Content-Type inválido: {file.content_type}")

    pdf_bytes = await file.read()
    if not pdf_bytes or len(pdf_bytes) < 50:
        raise HTTPException(status_code=400, detail="Arquivo vazio ou inválido")

    case_id = str(uuid.uuid4())

    # Cria registro inicial
    _CASES[case_id] = {
        "case_id": case_id,
        "case_type": case_type,
        "title": title,
        "status": "RECEBIDO",
        "last_error": None,
        "artifacts": None,
    }

    # Dispara pipeline
    background_tasks.add_task(_pipeline_process_case, case_id, pdf_bytes)

    return ProcessCaseResponse(case_id=case_id, status="RECEBIDO")


@router.get("/v1/cases/{case_id}/status")
async def case_status(case_id: str):
    item = _CASES.get(case_id)
    if not item:
        raise HTTPException(status_code=404, detail="case_id não encontrado")
    return {
        "case_id": case_id,
        "status": item["status"],
        "last_error": item["last_error"],
    }


@router.get("/v1/cases/{case_id}/artifacts")
async def case_artifacts(case_id: str):
    item = _CASES.get(case_id)
    if not item:
        raise HTTPException(status_code=404, detail="case_id não encontrado")

    if item["status"] in ("RECEBIDO", "PROCESSANDO"):
        raise HTTPException(status_code=409, detail="artifacts not ready")

    if item["status"] == "ERRO":
        raise HTTPException(status_code=500, detail=item["last_error"] or "erro no processamento")

    return item["artifacts"]
