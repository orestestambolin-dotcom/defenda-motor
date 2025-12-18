import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")  # pode trocar depois

SYSTEM_INSTRUCTIONS = """Você é um assistente jurídico (Brasil) para triagem.
Você NÃO substitui advogado. Gere saída objetiva e estruturada em JSON.
Foque em: execução bancária / CCB / confissão / monitória e prescrição intercorrente.
Se faltar dados, liste o que falta.
"""

async def analyze_legal_text(text: str) -> dict:
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY não configurada no Render."}

    payload = {
        "model": OPENAI_MODEL,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"TEXTO DO PROCESSO (extrato):\n{text}\n\n"}
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "triagem_juridica",
                "schema": {
                    "type": "object",
                    "properties": {
                        "resumo": {"type": "string"},
                        "tipo_acao_identificada": {"type": "string"},
                        "pontos_de_prescricao_intercorrente": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "pontos_de_nulidade_ou_defesas": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "dados_que_faltam": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "checklist_proximos_passos": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "grau_confianca_0a100": {"type": "integer"}
                    },
                    "required": [
                        "resumo",
                        "tipo_acao_identificada",
                        "pontos_de_prescricao_intercorrente",
                        "pontos_de_nulidade_ou_defesas",
                        "dados_que_faltam",
                        "checklist_proximos_passos",
                        "grau_confianca_0a100"
                    ],
                    "additionalProperties": False
                }
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    # O Responses API retorna o texto em output; aqui pegamos a saída já em JSON
    # (quando usamos json_schema, o modelo tende a retornar JSON válido)
    out = data.get("output", [])
    for item in out:
        if item.get("type") == "message":
            content = item.get("content", [])
            for c in content:
                if c.get("type") == "output_text":
                    import json
                    return json.loads(c.get("text", "{}"))

    return {"error": "Não consegui ler a resposta do modelo.", "raw": data}
