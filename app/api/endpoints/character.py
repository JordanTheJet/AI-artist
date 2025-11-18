"""Character comparison endpoints"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import logging

from app.models.schemas import CharacterComparisonResponse, BatchComparisonResponse, BatchComparisonItem
from app.services.character_comparison import CharacterComparison
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
character_service = CharacterComparison()


@router.post("/compare/character", response_model=CharacterComparisonResponse)
async def compare_character(
    image1: UploadFile = File(..., description="First image to compare"),
    image2: UploadFile = File(..., description="Second image to compare"),
):
    """
    Compare two images to determine if they contain the same character.

    This endpoint uses AI (CLIP) and perceptual hashing to analyze if two images
    show the same character, even if they're in different poses, angles, or contexts.

    **Parameters:**
    - **image1**: First image file (JPEG, PNG, etc.)
    - **image2**: Second image file (JPEG, PNG, etc.)

    **Returns:**
    - **is_match**: Whether the images show the same character
    - **similarity_score**: Similarity score from 0.0 to 1.0
    - **confidence**: Confidence level (low, medium, high)
    - **method**: Comparison method used
    - **message**: Human-readable result description
    """
    try:
        # Read image bytes
        image1_bytes = await image1.read()
        image2_bytes = await image2.read()

        # Validate file types
        if not image1.content_type or not image1.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="image1 must be an image file")
        if not image2.content_type or not image2.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="image2 must be an image file")

        # Perform comparison
        is_match, similarity, confidence = character_service.compare_characters(
            image1_bytes, image2_bytes, threshold=settings.character_similarity_threshold
        )

        # Build response message
        if is_match:
            message = f"The images likely show the same character (similarity: {similarity:.2%})"
        else:
            message = f"The images likely show different characters (similarity: {similarity:.2%})"

        return CharacterComparisonResponse(
            is_match=is_match,
            similarity_score=round(similarity, 4),
            confidence=confidence,
            method="CLIP + Perceptual Hashing",
            message=message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in character comparison endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during comparison")


@router.post("/compare/batch/character", response_model=BatchComparisonResponse)
async def compare_character_batch(
    reference_image: UploadFile = File(..., description="Reference image"),
    comparison_images: List[UploadFile] = File(..., description="Images to compare against reference"),
):
    """
    Compare one reference image with multiple images to find character matches.

    This endpoint is useful for finding which images in a collection show the same
    character as a reference image.

    **Parameters:**
    - **reference_image**: The reference image containing the character to find
    - **comparison_images**: List of images to compare (max 50)

    **Returns:**
    - **total_images**: Number of images compared
    - **matches**: List of matching images with their similarity scores
    - **best_match**: The best matching image (if any)
    - **method**: Comparison method used
    - **message**: Summary message
    """
    try:
        # Validate batch size
        if len(comparison_images) > settings.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Too many images. Maximum batch size is {settings.max_batch_size}",
            )

        if len(comparison_images) == 0:
            raise HTTPException(status_code=400, detail="No comparison images provided")

        # Validate file types
        if not reference_image.content_type or not reference_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="reference_image must be an image file")

        for idx, img in enumerate(comparison_images):
            if not img.content_type or not img.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail=f"comparison_images[{idx}] must be an image file"
                )

        # Read all images
        ref_bytes = await reference_image.read()
        comp_bytes_list = [await img.read() for img in comparison_images]

        # Perform batch comparison
        results = character_service.compare_character_batch(
            ref_bytes, comp_bytes_list, threshold=settings.character_similarity_threshold
        )

        # Build response
        matches = []
        for idx, similarity, is_match in results:
            if is_match:
                matches.append(
                    BatchComparisonItem(
                        image_index=idx, similarity_score=round(similarity, 4), is_match=True
                    )
                )

        # Get best match
        best_match = None
        if results:
            best_idx, best_sim, best_is_match = results[0]
            best_match = BatchComparisonItem(
                image_index=best_idx, similarity_score=round(best_sim, 4), is_match=best_is_match
            )

        # Build message
        if matches:
            message = f"Found {len(matches)} matching image(s) out of {len(comparison_images)}"
        else:
            message = f"No matching characters found in {len(comparison_images)} images"

        return BatchComparisonResponse(
            total_images=len(comparison_images),
            matches=matches,
            best_match=best_match,
            method="CLIP Batch Comparison",
            message=message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch character comparison endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during batch comparison")
