from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    platform_fee_percent: float = 3.0
    supabase_url: str
    supabase_service_role_key: str
    supabase_storage_bucket_portfolios: str = "portfolios"
    supabase_storage_bucket_deliverables: str = "deliverables"

    class Config:
        pass

settings = Settings()