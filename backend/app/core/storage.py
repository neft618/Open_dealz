from supabase import create_client, Client
from app.core.config import settings

_supabase_client: Client | None = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _supabase_client

async def upload_file(bucket: str, path: str, file_bytes: bytes, content_type: str) -> str:
    supabase = get_supabase()
    response = supabase.storage.from_(bucket).upload(path, file_bytes, {"content-type": content_type})
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.json()}")
    return supabase.storage.from_(bucket).get_public_url(path)

async def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    supabase = get_supabase()
    response = supabase.storage.from_(bucket).create_signed_url(path, expires_in)
    if "signedURL" not in response:
        raise Exception(f"Signed URL failed: {response}")
    return response["signedURL"]

async def delete_file(bucket: str, path: str):
    supabase = get_supabase()
    response = supabase.storage.from_(bucket).remove([path])
    if response.status_code != 200:
        raise Exception(f"Delete failed: {response.json()}")