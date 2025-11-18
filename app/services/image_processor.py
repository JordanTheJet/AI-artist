"""Image processing utilities"""

from PIL import Image
import io
import numpy as np
from typing import Union, List
import imagehash


class ImageProcessor:
    """Handles image loading, validation, and preprocessing"""

    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
        """
        Load an image from bytes

        Args:
            image_bytes: Raw image bytes

        Returns:
            PIL Image object

        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")

    @staticmethod
    def validate_image_size(image_bytes: bytes, max_size_mb: int = 10) -> bool:
        """
        Validate image file size

        Args:
            image_bytes: Raw image bytes
            max_size_mb: Maximum allowed size in megabytes

        Returns:
            True if valid, raises ValueError otherwise
        """
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(
                f"Image size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
            )
        return True

    @staticmethod
    def resize_image(image: Image.Image, max_dimension: int = 512) -> Image.Image:
        """
        Resize image while maintaining aspect ratio

        Args:
            image: PIL Image object
            max_dimension: Maximum width or height

        Returns:
            Resized PIL Image object
        """
        width, height = image.size

        if width <= max_dimension and height <= max_dimension:
            return image

        if width > height:
            new_width = max_dimension
            new_height = int((max_dimension / width) * height)
        else:
            new_height = max_dimension
            new_width = int((max_dimension / height) * width)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def get_perceptual_hash(image: Image.Image) -> imagehash.ImageHash:
        """
        Compute perceptual hash of an image

        Args:
            image: PIL Image object

        Returns:
            Perceptual hash
        """
        return imagehash.phash(image)

    @staticmethod
    def get_average_hash(image: Image.Image) -> imagehash.ImageHash:
        """
        Compute average hash of an image

        Args:
            image: PIL Image object

        Returns:
            Average hash
        """
        return imagehash.average_hash(image)

    @staticmethod
    def get_difference_hash(image: Image.Image) -> imagehash.ImageHash:
        """
        Compute difference hash of an image

        Args:
            image: PIL Image object

        Returns:
            Difference hash
        """
        return imagehash.dhash(image)

    @staticmethod
    def hash_similarity(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
        """
        Calculate similarity between two hashes (0-1 scale)

        Args:
            hash1: First image hash
            hash2: Second image hash

        Returns:
            Similarity score (0 = completely different, 1 = identical)
        """
        # Hamming distance measures differences
        distance = hash1 - hash2
        # Convert to similarity (max distance for 64-bit hash is 64)
        max_distance = len(hash1.hash) ** 2
        similarity = 1 - (distance / max_distance)
        return max(0.0, min(1.0, similarity))
