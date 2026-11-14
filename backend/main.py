"""Pre-Finance AI — FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from backend.config import settings
from backend.database import init_db, AsyncSessionLocal
from backend.models import User, SystemSetting
from backend.security.auth import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pre-finance-ai")


# ── Startup / shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Pre-Finance AI [{settings.ENVIRONMENT}]...")
    logger.info(f"Database: {'PostgreSQL' if settings.is_postgres else 'SQLite'}")
    await init_db()
    await seed_admin()
    logger.info("Ready ✓")
    yield
    logger.info("Shutting down.")


async def seed_admin():
    """Create admin account + default settings on first run."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.ADMIN_EMAIL.lower()))
        if result.scalar_one_or_none():
            return  # already seeded

        admin = User(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL.lower(),
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin)

        defaults = {
            "app_name":           "Pre-Finance AI",
            "allow_registration": "true",
            "max_upload_mb":      str(settings.MAX_FILE_SIZE_MB),
            "ai_model":           settings.OLLAMA_MODEL,
            "maintenance_mode":   "false",
        }
        for k, v in defaults.items():
            db.add(SystemSetting(key=k, value=v))

        await db.commit()
        logger.info(f"Admin seeded: {settings.ADMIN_EMAIL}")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Pre-Finance AI",
    description="Offline AI document intelligence platform.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from backend.routers import auth, users, documents, chat, admin  # noqa

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin.router)


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "ok",
        "app": "Pre-Finance AI",
        "environment": settings.ENVIRONMENT,
        "database": "postgresql" if settings.is_postgres else "sqlite",
    }


@app.get("/", tags=["System"])
async def root():
    return {"message": "Pre-Finance AI API is running.", "docs": "/docs"}
