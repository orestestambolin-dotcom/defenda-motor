from app.core.config import settings
import httpx

class LLMClient:
    async def complete_json(self, system: str, user: str) -> dict:
        if settings.llm_provider == "openai":
            return await self._openai(system, user)
        raise ValueError("LLM provider not configured")

    async def _openai(self, system: str, user: str) -> dict:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return _safe_json(data["choices"][0]["message"]["content"])

def _safe_json(s: str) -> dict:
    import json
    return json.loads(s)
