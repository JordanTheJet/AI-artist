"""Character comparison service"""

from PIL import Image
from typing import Tuple, List
import logging

from app.services.clip_service import CLIPService
from app.services.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class CharacterComparison:
    """Service for comparing characters in images"""

    def __init__(self):
        """Initialize the character comparison service"""
        self.clip_service = CLIPService()
        self.image_processor = ImageProcessor()

    def compare_characters(
        self, image1_bytes: bytes, image2_bytes: bytes, threshold: float = 0.75
    ) -> Tuple[bool, float, str]:
        """
        Compare two images to determine if they contain the same character

        Args:
            image1_bytes: First image as bytes
            image2_bytes: Second image as bytes
            threshold: Similarity threshold for matching (0-1)

        Returns:
            Tuple of (is_match, similarity_score, confidence_level)
        """
        try:
            # Validate and load images
            self.image_processor.validate_image_size(image1_bytes)
            self.image_processor.validate_image_size(image2_bytes)

            image1 = self.image_processor.load_image_from_bytes(image1_bytes)
            image2 = self.image_processor.load_image_from_bytes(image2_bytes)

            # Resize for faster processing
            image1 = self.image_processor.resize_image(image1)
            image2 = self.image_processor.resize_image(image2)

            # Use CLIP for semantic comparison
            similarity = self.clip_service.compare_images(image1, image2)

            # Also use perceptual hashing as a sanity check
            hash1 = self.image_processor.get_perceptual_hash(image1)
            hash2 = self.image_processor.get_perceptual_hash(image2)
            hash_similarity = self.image_processor.hash_similarity(hash1, hash2)

            # Combine both methods (weighted average)
            # CLIP is better for semantic understanding, so weight it higher
            combined_score = (similarity * 0.8) + (hash_similarity * 0.2)

            # Determine match
            is_match = combined_score >= threshold

            # Determine confidence level
            if combined_score >= 0.85:
                confidence = "high"
            elif combined_score >= 0.65:
                confidence = "medium"
            else:
                confidence = "low"

            logger.info(
                f"Character comparison: similarity={combined_score:.3f}, "
                f"match={is_match}, confidence={confidence}"
            )

            return is_match, combined_score, confidence

        except Exception as e:
            logger.error(f"Error in character comparison: {e}")
            raise

    def compare_character_batch(
        self, reference_bytes: bytes, comparison_bytes_list: List[bytes], threshold: float = 0.75
    ) -> List[Tuple[int, float, bool]]:
        """
        Compare one reference image with multiple images for character matching

        Args:
            reference_bytes: Reference image as bytes
            comparison_bytes_list: List of comparison images as bytes
            threshold: Similarity threshold for matching

        Returns:
            List of tuples (index, similarity_score, is_match)
        """
        try:
            # Load reference image
            self.image_processor.validate_image_size(reference_bytes)
            reference_image = self.image_processor.load_image_from_bytes(reference_bytes)
            reference_image = self.image_processor.resize_image(reference_image)

            # Load all comparison images
            comparison_images = []
            for img_bytes in comparison_bytes_list:
                self.image_processor.validate_image_size(img_bytes)
                img = self.image_processor.load_image_from_bytes(img_bytes)
                img = self.image_processor.resize_image(img)
                comparison_images.append(img)

            # Get similarities using CLIP
            similarities = self.clip_service.compare_one_to_many(
                reference_image, comparison_images
            )

            # Build results
            results = []
            for idx, similarity in enumerate(similarities):
                is_match = similarity >= threshold
                results.append((idx, similarity, is_match))

            # Sort by similarity (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            return results

        except Exception as e:
            logger.error(f"Error in batch character comparison: {e}")
            raise
