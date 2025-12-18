from pydantic import BaseModel, Field

class ProcessCaseRequest(BaseModel):
    case_id: str
    process_type: str  # EXECUCAO|MONITORIA
    title_type: str    # CCB|CONFISSAO|NAO_INFORMADO
    storage_provider: str = "supabase"
    storage_key: str

class StatusResponse(BaseModel):
    status: str
    progress: int = 0
    last_error: str | None = None
