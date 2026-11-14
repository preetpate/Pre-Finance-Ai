from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    # ── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Database ─────────────────────────────────────────────────────────────
    # Local dev  → sqlite+aiosqlite:///./data/prefinance.db
    # Supabase   → postgresql+asyncpg://user:pass@host:5432/postgres
    # Railway PG → postgresql+asyncpg://user:pass@host:5432/railway
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/prefinance.db"

    # ── Admin seed ────────────────────────────────────────────────────────────
    ADMIN_EMAIL: str = "admin@prefinance.ai"
    ADMIN_PASSWORD: str = "Admin@123456"
    ADMIN_NAME: str = "System Admin"

    # ── Ollama ────────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"

    # ── File storage ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "data/uploads"
    VECTOR_STORE_DIR: str = "data/vector_store"
    MAX_FILE_SIZE_MB: int = 50

    # ── Embedding ─────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins
    FRONTEND_ORIGIN: str = "http://localhost:5500"

    # ── Environment ───────────────────────────────────────────────────────────
    ENVIRONMENT: str = "development"   # development | production

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql")

    @property
    def allowed_origins(self) -> list[str]:
        base = [o.strip() for o in self.FRONTEND_ORIGIN.split(",")]
        base += ["http://localhost:5500", "http://127.0.0.1:5500"]
        return list(set(base))


settings = Settings()

# Only create local directories when using SQLite (not on cloud)
if not settings.is_postgres:
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.VECTOR_STORE_DIR).mkdir(parents=True, exist_ok=True)
