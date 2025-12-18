import enum
from sqlalchemy import String, DateTime, Enum, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base

class CaseStatus(str, enum.Enum):
    RECEBIDO = "RECEBIDO"
    PROCESSANDO = "PROCESSANDO"
    EM_REVISAO = "EM_REVISAO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"
    ERRO = "ERRO"

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    process_type: Mapped[str] = mapped_column(String)   # EXECUCAO|MONITORIA
    title_type: Mapped[str] = mapped_column(String)     # CCB|CONFISSAO|NAO_INFORMADO
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.RECEBIDO)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class CaseFile(Base):
    __tablename__ = "case_files"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(String, ForeignKey("cases.id"), index=True)
    storage_key: Mapped[str] = mapped_column(String)
    sha256: Mapped[str] = mapped_column(String)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)

class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    case_id: Mapped[str] = mapped_column(String, ForeignKey("cases.id"), index=True)
    kind: Mapped[str] = mapped_column(String)  # timeline_json|analysis_json|report_pdf
    storage_key: Mapped[str] = mapped_column(String)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
