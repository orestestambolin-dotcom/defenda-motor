from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from app.schemas.cases import ProcessCaseRequest, StatusResponse
from app.core.config import settings
from app.services.pipeline import Pipeline

router = APIRouter()
PIPE = Pipeline()

# status in-memory (MVP). Em produção: salvar no Postgres.
CASE_STATE: dict[str, dict] = {}

def _auth_webhook(x_webhook_secret: str | None):
    if not x_webhook_secret or x_webhook_secret != settings.webhook_shared_secret:
        raise HTTPException(status_code=401, detail="unauthorized")

@router.post("/cases/process")
async def process_case(payload: ProcessCaseRequest, bg: BackgroundTasks, x_webhook_secret: str | None = Header(default=None)):
    _auth_webhook(x_webhook_secret)

    CASE_STATE[payload.case_id] = {"status": "PROCESSANDO", "progress": 5, "last_error": None}

    async def _run():
        try:
            CASE_STATE[payload.case_id] = {"status": "PROCESSANDO", "progress": 15, "last_error": None}
            out = await PIPE.run(
                case_id=payload.case_id,
                storage_key=payload.storage_key,
                process_type=payload.process_type,
                title_type=payload.title_type,
            )
            CASE_STATE[payload.case_id] = {
                "status": "EM_REVISAO",
                "progress": 90,
                "last_error": None,
                "artifacts": out,
            }
        except Exception as e:
            CASE_STATE[payload.case_id] = {"status": "ERRO", "progress": 0, "last_error": str(e)}

    bg.add_task(_run)
    return {"accepted": True, "case_id": payload.case_id}

@router.get("/cases/{case_id}/status", response_model=StatusResponse)
async def case_status(case_id: str):
    st = CASE_STATE.get(case_id)
    if not st:
        return StatusResponse(status="RECEBIDO", progress=0, last_error=None)
    return StatusResponse(status=st["status"], progress=st["progress"], last_error=st.get("last_error"))

@router.get("/cases/{case_id}/artifacts")
async def case_artifacts(case_id: str):
    st = CASE_STATE.get(case_id)
    if not st or "artifacts" not in st:
        raise HTTPException(status_code=404, detail="artifacts not ready")
    arts = st["artifacts"]

    # gerar URLs assinadas
    from app.services.storage_supabase import SupabaseStorage
    s = SupabaseStorage()
    timeline_url = await s.signed_url(arts["timeline_key"], settings.signed_url_ttl_seconds)
    analysis_url = await s.signed_url(arts["analysis_key"], settings.signed_url_ttl_seconds)
    report_url = await s.signed_url(arts["report_key"], settings.signed_url_ttl_seconds)

    return {
        "timeline_json": timeline_url,
        "analysis_json": analysis_url,
        "report_pdf": report_url
    }
