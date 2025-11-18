"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "AI Artist - Image Comparison API"
    version: str = "0.1.0"
    api_prefix: str = "/api"

    # Model Settings
    clip_model_name: str = "clip-ViT-B-32"
    max_image_size_mb: int = 10

    # Comparison Thresholds
    character_similarity_threshold: float = 0.75
    style_similarity_threshold: float = 0.70

    # Performance
    max_batch_size: int = 50

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()
