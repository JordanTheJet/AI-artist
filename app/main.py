"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.endpoints import character, style
from app.models.schemas import HealthResponse
from app.services.clip_service import CLIPService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    AI-powered image comparison API for character recognition and visual style matching.

    ## Features

    * **Character Comparison**: Determine if two images show the same character
    * **Style Comparison**: Analyze if images share the same visual/artistic style
    * **Batch Processing**: Compare one image against many for efficient matching
    * **AI-Powered**: Uses CLIP (Contrastive Language-Image Pre-Training) for intelligent analysis

    ## Use Cases

    * Finding duplicate characters across image collections
    * Matching artistic styles in artwork databases
    * Content moderation and duplicate detection
    * Art style classification and matching
    """,
    docs_url="/",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event - preload CLIP model
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up AI Artist API...")
    try:
        # Initialize CLIP service (loads model)
        clip_service = CLIPService()
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        logger.warning("API will start but image comparisons may fail")


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint to verify API status and model availability.
    """
    try:
        clip_service = CLIPService()
        model_loaded = clip_service.is_model_loaded()
    except:
        model_loaded = False

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        version=settings.version,
        model_loaded=model_loaded,
    )


# Include routers
app.include_router(
    character.router,
    prefix=settings.api_prefix,
    tags=["Character Comparison"],
)

app.include_router(
    style.router,
    prefix=settings.api_prefix,
    tags=["Style Comparison"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
