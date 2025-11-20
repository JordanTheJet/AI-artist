# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Artist is an AI-powered image comparison system that provides two main capabilities: character recognition (determining if images show the same character) and visual style matching (analyzing if images share similar artistic styles).

The system is available in two forms:
1. **MCP Server** (`mcp_server.py`) - Direct integration with Claude Code via MCP protocol
2. **REST API** (`app/main.py`) - FastAPI server for general HTTP access

Both use the same underlying comparison services.

## Essential Commands

### MCP Server (for Claude Code)
```bash
# The MCP server is typically started automatically by Claude Code
# See MCP_SETUP.md for configuration instructions
python mcp_server.py
```

### REST API Server
```bash
python -m app.main
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API runs on port 8000 by default with interactive docs at http://localhost:8000/

### Testing
```bash
# Run the full test suite (requires server to be running)
python test_api.py

# Generate test images
python generate_test_images.py
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Important**: First run downloads the CLIP model (~350MB) which takes a few minutes. Subsequent runs are much faster.

## Architecture

### Core Design Pattern: Singleton CLIP Service

The CLIP model (sentence-transformers) is expensive to load (~1-2GB RAM, 1-2s load time), so `CLIPService` implements a singleton pattern to ensure the model is loaded exactly once and shared across all requests. This is critical for performance.

```python
# CLIPService maintains _instance and _model as class variables
# All endpoints reuse the same loaded model instance
```

### Request Flow

1. **API Layer** (`app/api/endpoints/`) - FastAPI routers handle HTTP requests, file uploads, and validation
2. **Service Layer** (`app/services/`) - Business logic for comparisons
   - `CharacterComparison` / `StyleComparison` - High-level comparison logic
   - `CLIPService` - AI model management (singleton)
   - `ImageProcessor` - Image loading, resizing, validation, perceptual hashing
3. **Configuration** (`app/core/config.py`) - Centralized settings using Pydantic

### Comparison Algorithms

**Character Comparison**:
- Uses CLIP embeddings (80% weight) + perceptual hashing (20% weight)
- Default threshold: 0.75
- Single comparisons use combined score; batch comparisons use CLIP only for efficiency

**Style Comparison**:
- Multi-factor approach:
  - CLIP semantic similarity (35%)
  - Color palette similarity via k-means clustering (35%)
  - Brightness similarity (10%)
  - Saturation similarity (10%)
  - Edge density similarity (10%)
- Default threshold: 0.70

### Image Processing Pipeline

All images go through `ImageProcessor`:
1. Size validation (max 10MB by default, configurable via `MAX_IMAGE_SIZE_MB`)
2. Load from bytes using PIL
3. Resize to max 800x800 for efficient processing (preserves aspect ratio)
4. Convert to RGB if needed

## Configuration

Settings are defined in `app/core/config.py` using Pydantic and can be overridden via `.env` file:

```env
# Model settings
CLIP_MODEL_NAME="clip-ViT-B-32"
MAX_IMAGE_SIZE_MB=10

# Thresholds
CHARACTER_SIMILARITY_THRESHOLD=0.75
STYLE_SIMILARITY_THRESHOLD=0.70

# Performance
MAX_BATCH_SIZE=50
```

## API Endpoints Structure

All endpoints are prefixed with `/api` (configurable):

- `POST /api/compare/character` - Compare two images for same character
- `POST /api/compare/batch/character` - Compare one reference vs multiple images
- `POST /api/compare/style` - Compare two images for same style
- `POST /api/compare/batch/style` - Batch style comparison
- `GET /health` - Health check with model status

Endpoints use FastAPI's file upload via `UploadFile` and return Pydantic models defined in `app/models/schemas.py`.

## Key Dependencies

- **FastAPI + Uvicorn** - Web framework and ASGI server
- **sentence-transformers** - Provides CLIP model
- **torch + torchvision** - PyTorch backend for CLIP
- **Pillow** - Image loading and manipulation
- **OpenCV (cv2)** - Computer vision operations (k-means for color palette, edge detection)
- **imagehash** - Perceptual hashing for character comparison

## Performance Considerations

- **First request latency**: 1-2s for CLIP model loading (if not preloaded at startup)
- **Subsequent requests**: 100-500ms typical response time
- **Memory usage**: ~1-2GB for CLIP model
- **Batch operations**: More efficient than multiple individual requests
- The startup event in `app/main.py` preloads the CLIP model to avoid first-request delays

## Important Implementation Details

1. **Singleton Pattern**: Never instantiate multiple `CLIPService` instances - the class handles this automatically
2. **Image Format**: Always convert images to RGB before processing (handled by `ImageProcessor`)
3. **Error Handling**: All service methods raise exceptions that are caught by endpoint handlers and converted to appropriate HTTP responses
4. **CORS**: Currently set to allow all origins (`["*"]`) - should be configured for production
5. **Batch Size Limits**: Enforced at endpoint level, configurable via `settings.max_batch_size`

## MCP Server Integration

The MCP server (`mcp_server.py`) provides direct Claude Code integration. It exposes four tools:
- `compare_characters` - Compare two images for same character
- `compare_styles` - Compare two images for same style
- `batch_compare_characters` - Compare one reference vs multiple images (character)
- `batch_compare_styles` - Compare one reference vs multiple images (style)

**Setup**: See `MCP_SETUP.md` for detailed configuration instructions.

**Key differences from REST API**:
- Uses file paths instead of HTTP uploads
- Returns formatted text output instead of JSON
- Started automatically by Claude Code (no manual server start needed)
- Same underlying services (`CharacterComparison`, `StyleComparison`, `CLIPService`)
