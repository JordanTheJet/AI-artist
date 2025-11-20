"""Pydantic schemas for API responses"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether CLIP model is loaded")


class CharacterComparisonResponse(BaseModel):
    """Response for character comparison"""
    is_match: bool = Field(..., description="Whether images show the same character")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score between 0 and 1")
    confidence: str = Field(..., description="Confidence level: low, medium, or high")
    method: str = Field(..., description="Comparison method used")
    message: str = Field(..., description="Human-readable result description")


class StyleComparisonResponse(BaseModel):
    """Response for style comparison"""
    is_match: bool = Field(..., description="Whether images have matching styles")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score between 0 and 1")
    confidence: str = Field(..., description="Confidence level: low, medium, or high")
    method: str = Field(..., description="Comparison method used")
    style_features: Dict[str, float] = Field(..., description="Detailed style feature similarities")
    message: str = Field(..., description="Human-readable result description")


class BatchComparisonItem(BaseModel):
    """Single item in batch comparison results"""
    image_index: int = Field(..., description="Index of the comparison image")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    is_match: bool = Field(..., description="Whether this image matches the reference")


class BatchComparisonResponse(BaseModel):
    """Response for batch comparison"""
    total_images: int = Field(..., description="Total number of images compared")
    matches: List[BatchComparisonItem] = Field(..., description="List of matching images")
    best_match: Optional[BatchComparisonItem] = Field(None, description="Best matching image")
    method: str = Field(..., description="Comparison method used")
    message: str = Field(..., description="Summary message")
