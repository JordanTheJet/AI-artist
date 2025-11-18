"""CLIP-based image comparison service"""

from sentence_transformers import SentenceTransformer, util
from PIL import Image
import torch
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class CLIPService:
    """Service for CLIP-based image embeddings and comparisons"""

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super(CLIPService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize CLIP model"""
        if self._model is None:
            logger.info("Loading CLIP model...")
            try:
                self._model = SentenceTransformer("clip-ViT-B-32")
                logger.info("CLIP model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load CLIP model: {e}")
                raise

    @property
    def model(self) -> SentenceTransformer:
        """Get the loaded model"""
        return self._model

    def get_image_embedding(self, image: Image.Image) -> np.ndarray:
        """
        Get CLIP embedding for an image

        Args:
            image: PIL Image object

        Returns:
            Image embedding as numpy array
        """
        try:
            embedding = self._model.encode(image, convert_to_tensor=False)
            return embedding
        except Exception as e:
            logger.error(f"Failed to get image embedding: {e}")
            raise

    def get_batch_embeddings(self, images: List[Image.Image]) -> List[np.ndarray]:
        """
        Get CLIP embeddings for multiple images

        Args:
            images: List of PIL Image objects

        Returns:
            List of image embeddings
        """
        try:
            embeddings = self._model.encode(images, convert_to_tensor=False)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to get batch embeddings: {e}")
            raise

    def calculate_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First image embedding
            embedding2: Second image embedding

        Returns:
            Similarity score (0-1)
        """
        # Convert to tensors for util.cos_sim
        tensor1 = torch.from_numpy(embedding1)
        tensor2 = torch.from_numpy(embedding2)

        similarity = util.cos_sim(tensor1, tensor2)
        return float(similarity.item())

    def compare_images(self, image1: Image.Image, image2: Image.Image) -> float:
        """
        Compare two images and return similarity score

        Args:
            image1: First PIL Image
            image2: Second PIL Image

        Returns:
            Similarity score (0-1)
        """
        emb1 = self.get_image_embedding(image1)
        emb2 = self.get_image_embedding(image2)
        return self.calculate_similarity(emb1, emb2)

    def compare_one_to_many(
        self, reference_image: Image.Image, comparison_images: List[Image.Image]
    ) -> List[float]:
        """
        Compare one reference image to many images

        Args:
            reference_image: The reference PIL Image
            comparison_images: List of PIL Images to compare against

        Returns:
            List of similarity scores
        """
        # Get reference embedding
        ref_embedding = self.get_image_embedding(reference_image)

        # Get all comparison embeddings at once
        comp_embeddings = self.get_batch_embeddings(comparison_images)

        # Calculate similarities
        similarities = []
        for comp_emb in comp_embeddings:
            similarity = self.calculate_similarity(ref_embedding, comp_emb)
            similarities.append(similarity)

        return similarities

    def is_model_loaded(self) -> bool:
        """Check if the model is loaded"""
        return self._model is not None
