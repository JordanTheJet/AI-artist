"""Visual style comparison service"""

from PIL import Image
import numpy as np
from typing import Tuple, List, Dict
import logging
import cv2

from app.services.clip_service import CLIPService
from app.services.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class StyleComparison:
    """Service for comparing visual styles in images"""

    def __init__(self):
        """Initialize the style comparison service"""
        self.clip_service = CLIPService()
        self.image_processor = ImageProcessor()

    def extract_color_palette(self, image: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from an image

        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract

        Returns:
            List of RGB tuples
        """
        # Resize for faster processing
        img_small = image.resize((150, 150))
        img_array = np.array(img_small)

        # Reshape to list of pixels
        pixels = img_array.reshape(-1, 3)

        # Use k-means to find dominant colors
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, palette = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Convert to int tuples
        palette = palette.astype(int)
        return [tuple(color) for color in palette]

    def calculate_color_similarity(
        self, palette1: List[Tuple[int, int, int]], palette2: List[Tuple[int, int, int]]
    ) -> float:
        """
        Calculate similarity between two color palettes

        Args:
            palette1: First color palette
            palette2: Second color palette

        Returns:
            Similarity score (0-1)
        """
        # Convert to numpy arrays
        p1 = np.array(palette1)
        p2 = np.array(palette2)

        # Calculate pairwise distances
        min_distances = []
        for color1 in p1:
            distances = np.linalg.norm(p2 - color1, axis=1)
            min_distances.append(np.min(distances))

        # Average minimum distance
        avg_distance = np.mean(min_distances)

        # Normalize to 0-1 (max distance in RGB space is ~442)
        similarity = 1 - (avg_distance / 442)
        return max(0.0, min(1.0, similarity))

    def get_style_features(self, image: Image.Image) -> Dict[str, any]:
        """
        Extract style features from an image

        Args:
            image: PIL Image object

        Returns:
            Dictionary of style features
        """
        # Extract color palette
        palette = self.extract_color_palette(image)

        # Convert to OpenCV format for additional analysis
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Calculate average brightness
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        avg_brightness = np.mean(hsv[:, :, 2])

        # Calculate average saturation
        avg_saturation = np.mean(hsv[:, :, 1])

        # Edge density (measure of detail/style complexity)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        return {
            "palette": palette,
            "brightness": float(avg_brightness),
            "saturation": float(avg_saturation),
            "edge_density": float(edge_density),
        }

    def compare_styles(
        self, image1_bytes: bytes, image2_bytes: bytes, threshold: float = 0.70
    ) -> Tuple[bool, float, str, Dict]:
        """
        Compare two images to determine if they have the same visual style

        Args:
            image1_bytes: First image as bytes
            image2_bytes: Second image as bytes
            threshold: Similarity threshold for matching (0-1)

        Returns:
            Tuple of (is_match, similarity_score, confidence_level, style_features)
        """
        try:
            # Validate and load images
            self.image_processor.validate_image_size(image1_bytes)
            self.image_processor.validate_image_size(image2_bytes)

            image1 = self.image_processor.load_image_from_bytes(image1_bytes)
            image2 = self.image_processor.load_image_from_bytes(image2_bytes)

            # Resize for consistent processing
            image1 = self.image_processor.resize_image(image1)
            image2 = self.image_processor.resize_image(image2)

            # Extract style features
            features1 = self.get_style_features(image1)
            features2 = self.get_style_features(image2)

            # CLIP semantic similarity (captures overall style)
            clip_similarity = self.clip_service.compare_images(image1, image2)

            # Color palette similarity
            color_similarity = self.calculate_color_similarity(
                features1["palette"], features2["palette"]
            )

            # Brightness similarity
            brightness_diff = abs(features1["brightness"] - features2["brightness"]) / 255.0
            brightness_similarity = 1 - brightness_diff

            # Saturation similarity
            saturation_diff = abs(features1["saturation"] - features2["saturation"]) / 255.0
            saturation_similarity = 1 - saturation_diff

            # Edge density similarity
            edge_diff = abs(features1["edge_density"] - features2["edge_density"])
            edge_similarity = 1 - edge_diff

            # Weighted combination for style similarity
            # Color and CLIP are most important for style
            combined_score = (
                clip_similarity * 0.35
                + color_similarity * 0.35
                + brightness_similarity * 0.10
                + saturation_similarity * 0.10
                + edge_similarity * 0.10
            )

            # Determine match
            is_match = combined_score >= threshold

            # Determine confidence level
            if combined_score >= 0.80:
                confidence = "high"
            elif combined_score >= 0.60:
                confidence = "medium"
            else:
                confidence = "low"

            # Build style features report
            style_report = {
                "color_similarity": round(color_similarity, 3),
                "brightness_similarity": round(brightness_similarity, 3),
                "saturation_similarity": round(saturation_similarity, 3),
                "semantic_similarity": round(clip_similarity, 3),
            }

            logger.info(
                f"Style comparison: similarity={combined_score:.3f}, "
                f"match={is_match}, confidence={confidence}"
            )

            return is_match, combined_score, confidence, style_report

        except Exception as e:
            logger.error(f"Error in style comparison: {e}")
            raise

    def compare_style_batch(
        self, reference_bytes: bytes, comparison_bytes_list: List[bytes], threshold: float = 0.70
    ) -> List[Tuple[int, float, bool]]:
        """
        Compare one reference image with multiple images for style matching

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

            # Get reference features
            ref_features = self.get_style_features(reference_image)
            ref_palette = ref_features["palette"]

            # Load all comparison images
            comparison_images = []
            for img_bytes in comparison_bytes_list:
                self.image_processor.validate_image_size(img_bytes)
                img = self.image_processor.load_image_from_bytes(img_bytes)
                img = self.image_processor.resize_image(img)
                comparison_images.append(img)

            # Get CLIP similarities
            clip_similarities = self.clip_service.compare_one_to_many(
                reference_image, comparison_images
            )

            # Build results
            results = []
            for idx, (img, clip_sim) in enumerate(zip(comparison_images, clip_similarities)):
                # Get color similarity
                comp_features = self.get_style_features(img)
                color_sim = self.calculate_color_similarity(ref_palette, comp_features["palette"])

                # Combined score (simplified for batch)
                combined_score = (clip_sim * 0.6) + (color_sim * 0.4)

                is_match = combined_score >= threshold
                results.append((idx, combined_score, is_match))

            # Sort by similarity (descending)
            results.sort(key=lambda x: x[1], reverse=True)

            return results

        except Exception as e:
            logger.error(f"Error in batch style comparison: {e}")
            raise
