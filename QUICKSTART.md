# Quick Start Guide

## Installation Status

The API dependencies are currently installing. This can take 15-30 minutes due to large packages like PyTorch and CLIP.

## Once Installation Completes

### 1. Verify Installation

```bash
pip list | grep -E "(torch|fastapi|sentence)"
```

You should see:
- fastapi
- torch
- sentence-transformers
- and other packages

### 2. Start the API Server

```bash
python -m app.main
```

The server will start on http://localhost:8000

**Note**: The first startup will download the CLIP model (~350MB), which may take a few minutes.

### 3. Test the API

Open your browser to http://localhost:8000 to see the interactive API documentation.

Or run the automated test suite:

```bash
# In a new terminal (while the server is running)
python test_api.py
```

### 4. Manual Testing

Test images have been generated in the `test_images/` directory:

**Character Comparison:**
```bash
curl -X POST "http://localhost:8000/api/compare/character" \
  -F "image1=@test_images/character1_blue.jpg" \
  -F "image2=@test_images/character1_red.jpg"
```

**Style Comparison:**
```bash
curl -X POST "http://localhost:8000/api/compare/style" \
  -F "image1=@test_images/style1_blue_stripes.jpg" \
  -F "image2=@test_images/style1_blue_stripes2.jpg"
```

## Troubleshooting

### If installation fails:

1. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Try installing packages individually:**
   ```bash
   pip install fastapi uvicorn python-multipart
   pip install torch torchvision
   pip install sentence-transformers
   pip install opencv-python imagehash
   ```

3. **Use CPU-only PyTorch (smaller, faster):**
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```

### If the server won't start:

1. Check if all packages are installed:
   ```bash
   python -c "import fastapi, torch, sentence_transformers; print('All packages OK')"
   ```

2. Check for port conflicts:
   ```bash
   lsof -i :8000  # See if port 8000 is in use
   ```

3. Try a different port:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

### Memory Issues:

If you get out of memory errors:
- Close other applications
- Use smaller batch sizes (edit `MAX_BATCH_SIZE` in `.env`)
- Consider using a machine with more RAM (2GB+ recommended)

## Next Steps

Once the API is running successfully:

1. Try it with your own images
2. Adjust thresholds in `.env` file
3. Integrate it into your application
4. Check the full README.md for more details

## Test Images

The `test_images/` directory contains:
- **Character images**: Circle and square characters in different colors
- **Style images**: Images with different patterns and color schemes

These are simple generated images for testing. The API will work much better with real photos and artwork!
