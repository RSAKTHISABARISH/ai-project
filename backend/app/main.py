import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import Base, engine, SessionLocal
from app.data.synthetic_generator import seed_database
from app.api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix2runbook")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed initial synthetic dataset if empty
    db = SessionLocal()
    try:
        counts = seed_database(db, force_reset=False)
        logger.info(f"Database ready with {counts['incidents']} incidents, {counts['events']} events.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()
    
    yield
    logger.info("Shutting down Fix2Runbook backend...")

app = FastAPI(
    title="Fix2Runbook API",
    description="Evidence-Driven ERP Maintenance Knowledge Capture Assistant API",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct root health endpoint for convenience
@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
