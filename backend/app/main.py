import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.auth import router as auth_router
from backend.app.api.crop import router as crop_router
from backend.app.api.disease import router as disease_router
from backend.app.api.products import router as products_router
from backend.app.api.chatbot import router as chatbot_router
from backend.app.api.voice import router as voice_router
from backend.app.api.analytics import router as analytics_router

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description="Scalable biological agricultural platform for Vishakan Biotech Pvt Ltd, Coimbatore, Tamil Nadu.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred on the server. Please check server logs."}
    )

# Startup Event: Setup tables and trigger database/Chroma vector seeding if empty
@app.on_event("startup")
def startup_db_setup():
    logger.info("Starting up FastAPI database verification...")
    try:
        # Create database tables if they do not exist
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL database tables verified.")
        
        # Trigger seeding script automatically if products are empty
        from backend.seed import seed_database, seed_chromadb
        seed_database()
        seed_chromadb()
    except Exception as e:
        logger.error(f"Failed to complete database setup during startup: {e}")

# Include Sub-Routers
app.include_router(auth_router, prefix="/api")
app.include_router(crop_router, prefix="/api")
app.include_router(disease_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint for the Vishakan Biotech platform backend.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database_connected": True
    }
