# AI Artist - Image Comparison API

An AI-powered image comparison system for intelligent character recognition and visual style matching.

**Available as:**
- 🔌 **MCP Server** - Direct integration with Claude Code ([setup guide](MCP_SETUP.md))
- 🌐 **REST API** - HTTP API for general use (documented below)

## Features

### Character Comparison
- **Single Comparison**: Compare two images to determine if they show the same character
- **Batch Comparison**: Compare one reference image against multiple images to find character matches
- Uses CLIP (Contrastive Language-Image Pre-Training) + perceptual hashing for robust matching

### Visual Style Comparison
- **Single Comparison**: Analyze if two images share the same artistic or visual style
- **Batch Comparison**: Find images with matching styles from a collection
- Analyzes color palettes, brightness, saturation, and semantic features

## Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **CLIP (via sentence-transformers)**: State-of-the-art AI model for image understanding
- **OpenCV**: Advanced computer vision processing
- **Pillow**: Image handling and manipulation
- **ImageHash**: Perceptual hashing for duplicate detection

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/JordanTheJet/AI-artist.git
cd AI-artist
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: First run will download the CLIP model (~350MB), which may take a few minutes.

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Endpoint**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/ (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

### API Endpoints

#### Character Comparison

**Compare Two Images for Same Character**
```bash
POST /api/compare/character
```

Example using curl:
```bash
curl -X POST "http://localhost:8000/api/compare/character" \
  -F "image1=@path/to/image1.jpg" \
  -F "image2=@path/to/image2.jpg"
```

Response:
```json
{
  "is_match": true,
  "similarity_score": 0.8543,
  "confidence": "high",
  "method": "CLIP + Perceptual Hashing",
  "message": "The images likely show the same character (similarity: 85.43%)"
}
```

**Batch Character Comparison**
```bash
POST /api/compare/batch/character
```

Example:
```bash
curl -X POST "http://localhost:8000/api/compare/batch/character" \
  -F "reference_image=@reference.jpg" \
  -F "comparison_images=@image1.jpg" \
  -F "comparison_images=@image2.jpg" \
  -F "comparison_images=@image3.jpg"
```

Response:
```json
{
  "total_images": 3,
  "matches": [
    {"image_index": 0, "similarity_score": 0.8912, "is_match": true},
    {"image_index": 2, "similarity_score": 0.7834, "is_match": true}
  ],
  "best_match": {"image_index": 0, "similarity_score": 0.8912, "is_match": true},
  "method": "CLIP Batch Comparison",
  "message": "Found 2 matching image(s) out of 3"
}
```

#### Style Comparison

**Compare Two Images for Same Style**
```bash
POST /api/compare/style
```

Example:
```bash
curl -X POST "http://localhost:8000/api/compare/style" \
  -F "image1=@style1.jpg" \
  -F "image2=@style2.jpg"
```

Response:
```json
{
  "is_match": true,
  "similarity_score": 0.7892,
  "confidence": "high",
  "method": "CLIP + Color Analysis + Style Features",
  "style_features": {
    "color_similarity": 0.823,
    "brightness_similarity": 0.756,
    "saturation_similarity": 0.801,
    "semantic_similarity": 0.789
  },
  "message": "The images have similar visual styles (similarity: 78.92%)"
}
```

**Batch Style Comparison**
```bash
POST /api/compare/batch/style
```

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "model_loaded": true
}
```

## Configuration

You can customize settings by creating a `.env` file:

```env
# API Settings
APP_NAME="AI Artist - Image Comparison API"
API_PREFIX="/api"

# Model Settings
CLIP_MODEL_NAME="clip-ViT-B-32"
MAX_IMAGE_SIZE_MB=10

# Comparison Thresholds
CHARACTER_SIMILARITY_THRESHOLD=0.75
STYLE_SIMILARITY_THRESHOLD=0.70

# Performance
MAX_BATCH_SIZE=50
```

## API Limits

- Maximum image size: 10 MB (configurable)
- Maximum batch size: 50 images (configurable)
- Supported formats: JPEG, PNG, GIF, BMP, WebP

## How It Works

### Character Comparison
1. **Image Processing**: Images are loaded and resized for efficient processing
2. **CLIP Analysis**: The CLIP model generates semantic embeddings that understand visual content
3. **Perceptual Hashing**: Fast hashing provides a sanity check for visual similarity
4. **Combined Score**: Results are weighted (80% CLIP, 20% hash) for optimal accuracy
5. **Threshold Matching**: Scores above the threshold (default 0.75) indicate a match

### Style Comparison
1. **Feature Extraction**: Analyzes color palette, brightness, saturation, and edge density
2. **CLIP Semantic Analysis**: Understands artistic style and composition
3. **Color Analysis**: Extracts and compares dominant color palettes
4. **Style Metrics**: Evaluates brightness, saturation, and detail levels
5. **Weighted Scoring**: Combines multiple factors for comprehensive style matching

## Use Cases

- **Art Collections**: Find similar artworks or match artistic styles
- **Content Moderation**: Detect duplicate or similar images
- **E-commerce**: Group products by visual similarity
- **Media Libraries**: Organize photos by subjects or artistic style
- **Character Recognition**: Match characters across different scenes/contexts

## Project Structure

```
AI-artist/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── character.py       # Character comparison endpoints
│   │       └── style.py           # Style comparison endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── clip_service.py        # CLIP model service
│       ├── image_processor.py     # Image processing utilities
│       ├── character_comparison.py # Character comparison logic
│       └── style_comparison.py     # Style comparison logic
├── requirements.txt
├── .gitignore
└── README.md
```

## Development

### Running Tests
```bash
# Coming soon
pytest tests/
```

### Code Formatting
```bash
black app/
isort app/
```

## Performance Considerations

- **First Request**: The initial request may be slower as the CLIP model loads into memory (~1-2 seconds)
- **Subsequent Requests**: Fast response times (typically 100-500ms per comparison)
- **Batch Processing**: More efficient than individual comparisons for multiple images
- **Memory**: Approximately 1-2 GB RAM required for the CLIP model

## Troubleshooting

### Model Download Issues
If the CLIP model fails to download:
```bash
# Clear cache and retry
rm -rf ~/.cache/torch/sentence_transformers/
python -m app.main
```

### Out of Memory
If you encounter memory issues:
- Reduce `MAX_BATCH_SIZE` in configuration
- Ensure images are reasonably sized (API automatically resizes large images)
- Consider using a smaller CLIP model variant

## Future Enhancements

- [ ] Support for video frame comparison
- [ ] Face detection and matching
- [ ] Style transfer suggestions
- [ ] Caching for improved performance
- [ ] Database integration for result storage
- [ ] Rate limiting and authentication
- [ ] Async batch processing for large datasets

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
