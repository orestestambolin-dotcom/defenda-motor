import httpx
from app.core.config import settings

class SupabaseStorage:
    def __init__(self):
        self.base = settings.supabase_url.rstrip("/")
        self.key = settings.supabase_service_role_key
        self.bucket = settings.supabase_storage_bucket

    async def download_bytes(self, storage_key: str) -> bytes:
        url = f"{self.base}/storage/v1/object/{self.bucket}/{storage_key}"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.get(url, headers={"Authorization": f"Bearer {self.key}"})
            r.raise_for_status()
            return r.content

    async def upload_bytes(self, storage_key: str, data: bytes, content_type: str):
        url = f"{self.base}/storage/v1/object/{self.bucket}/{storage_key}"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Content-Type": content_type,
                    "x-upsert": "true",
                },
                content=data,
            )
            r.raise_for_status()

    async def signed_url(self, storage_key: str, ttl: int) -> str:
        url = f"{self.base}/storage/v1/object/sign/{self.bucket}/{storage_key}"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.key}"},
                json={"expiresIn": ttl},
            )
            r.raise_for_status()
            return r.json().get("signedURL")
