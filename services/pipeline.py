import json
from app.services.storage_supabase import SupabaseStorage
from app.services.pdf_text import extract_text
from app.services.llm import LLMClient
from app.services.report import build_report_pdf

class Pipeline:
    def __init__(self):
        self.storage = SupabaseStorage()
        self.llm = LLMClient()

    async def run(self, case_id: str, storage_key: str, process_type: str, title_type: str):
        # 1) download
        pdf_bytes = await self.storage.download_bytes(storage_key)

        # 2) extract text (MVP: sem OCR)
        text, pages = extract_text(pdf_bytes)

        # 3) timeline (JSON)
        system = "Você é um analista jurídico. Responda SOMENTE em JSON."
        user_timeline = f"""
Construa uma timeline processual a partir do texto abaixo.
Inclua SOMENTE eventos com data explícita.
Para cada evento, inclua página quando possível (se não houver, use null).
Contexto: process_type={process_type}, title_type={title_type}

TEXTO:
{text[:120000]}
"""
        timeline = await self.llm.complete_json(system, user_timeline)

        # 4) analysis (JSON)
        user_analysis = f"""
Com base na timeline abaixo, sugira teses defensivas possíveis (prescrição intercorrente, nulidades, exigibilidade do título).
Marque incertezas quando faltar evidência. Responda em JSON.

TIMELINE:
{json.dumps(timeline)[:120000]}
"""
        analysis = await self.llm.complete_json(system, user_analysis)

        # 5) report pdf
        summary = {"headline": "Diagnóstico jurídico com base nos documentos enviados."}
        pdf_out = build_report_pdf(case_id, summary, timeline, analysis)

        # 6) upload artifacts
        base = f"private/artifacts/{case_id}"
        timeline_key = f"{base}/timeline.json"
        analysis_key = f"{base}/analysis.json"
        report_key = f"{base}/relatorio.pdf"

        await self.storage.upload_bytes(timeline_key, json.dumps(timeline).encode("utf-8"), "application/json")
        await self.storage.upload_bytes(analysis_key, json.dumps(analysis).encode("utf-8"), "application/json")
        await self.storage.upload_bytes(report_key, pdf_out, "application/pdf")

        return {
            "pages": pages,
            "timeline_key": timeline_key,
            "analysis_key": analysis_key,
            "report_key": report_key
        }
