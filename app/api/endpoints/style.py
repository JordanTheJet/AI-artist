"""Visual style comparison endpoints"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import logging

from app.models.schemas import StyleComparisonResponse, BatchComparisonResponse, BatchComparisonItem
from app.services.style_comparison import StyleComparison
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
style_service = StyleComparison()


@router.post("/compare/style", response_model=StyleComparisonResponse)
async def compare_style(
    image1: UploadFile = File(..., description="First image to compare"),
    image2: UploadFile = File(..., description="Second image to compare"),
):
    """
    Compare two images to determine if they have the same visual style.

    This endpoint analyzes color palettes, brightness, saturation, and semantic
    features to determine if two images share the same artistic or visual style.

    **Parameters:**
    - **image1**: First image file (JPEG, PNG, etc.)
    - **image2**: Second image file (JPEG, PNG, etc.)

    **Returns:**
    - **is_match**: Whether the images have matching visual styles
    - **similarity_score**: Similarity score from 0.0 to 1.0
    - **confidence**: Confidence level (low, medium, high)
    - **method**: Comparison method used
    - **style_features**: Detailed breakdown of style similarities
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
        is_match, similarity, confidence, style_features = style_service.compare_styles(
            image1_bytes, image2_bytes, threshold=settings.style_similarity_threshold
        )

        # Build response message
        if is_match:
            message = f"The images have similar visual styles (similarity: {similarity:.2%})"
        else:
            message = f"The images have different visual styles (similarity: {similarity:.2%})"

        return StyleComparisonResponse(
            is_match=is_match,
            similarity_score=round(similarity, 4),
            confidence=confidence,
            method="CLIP + Color Analysis + Style Features",
            style_features=style_features,
            message=message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in style comparison endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during comparison")


@router.post("/compare/batch/style", response_model=BatchComparisonResponse)
async def compare_style_batch(
    reference_image: UploadFile = File(..., description="Reference image with target style"),
    comparison_images: List[UploadFile] = File(..., description="Images to compare against reference"),
):
    """
    Compare one reference image with multiple images to find style matches.

    This endpoint is useful for finding which images in a collection have the same
    visual or artistic style as a reference image.

    **Parameters:**
    - **reference_image**: The reference image with the target style
    - **comparison_images**: List of images to compare (max 50)

    **Returns:**
    - **total_images**: Number of images compared
    - **matches**: List of images with matching styles and their similarity scores
    - **best_match**: The best style match (if any)
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
        results = style_service.compare_style_batch(
            ref_bytes, comp_bytes_list, threshold=settings.style_similarity_threshold
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
            message = f"Found {len(matches)} image(s) with matching style out of {len(comparison_images)}"
        else:
            message = f"No matching styles found in {len(comparison_images)} images"

        return BatchComparisonResponse(
            total_images=len(comparison_images),
            matches=matches,
            best_match=best_match,
            method="CLIP + Color Palette Batch Comparison",
            message=message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch style comparison endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during batch comparison")
