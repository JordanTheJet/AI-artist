# MCP Server Setup Guide

This guide explains how to set up and use the AI Artist MCP (Model Context Protocol) server with Claude Code.

## What is an MCP Server?

An MCP server allows Claude Code to directly access the AI Artist image comparison functionality without needing to run a REST API server. Claude Code can call the image comparison tools just like any other built-in tool.

## Installation

### 1. Install MCP Dependencies

```bash
pip install mcp>=1.0.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure Claude Code

Add the MCP server to your Claude Code configuration. The configuration file location depends on your system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the following to your configuration file:

```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "python",
      "args": [
        "/absolute/path/to/AI-artist/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

**Important**: Replace `/absolute/path/to/AI-artist/` with the actual absolute path to this repository.

### 3. Restart Claude Code

After updating the configuration, restart Claude Code to load the MCP server.

## Available Tools

Once configured, Claude Code will have access to these tools:

### 1. `compare_characters`

Compare two images to determine if they show the same character.

**Parameters:**
- `image1_path` (required): Path to the first image file
- `image2_path` (required): Path to the second image file
- `threshold` (optional): Similarity threshold (0-1), default: 0.75

**Example:**
```
Compare these two images to see if they show the same character:
- /path/to/character1.jpg
- /path/to/character2.jpg
```

### 2. `compare_styles`

Compare two images to determine if they have the same visual/artistic style.

**Parameters:**
- `image1_path` (required): Path to the first image file
- `image2_path` (required): Path to the second image file
- `threshold` (optional): Similarity threshold (0-1), default: 0.70

**Example:**
```
Check if these two images have similar artistic styles:
- /path/to/artwork1.jpg
- /path/to/artwork2.jpg
```

### 3. `batch_compare_characters`

Compare one reference image with multiple images to find character matches.

**Parameters:**
- `reference_image_path` (required): Path to the reference image
- `comparison_image_paths` (required): Array of paths to images to compare
- `threshold` (optional): Similarity threshold (0-1), default: 0.75

**Example:**
```
Find all images that show the same character as reference.jpg from this collection:
- image1.jpg
- image2.jpg
- image3.jpg
```

### 4. `batch_compare_styles`

Compare one reference image with multiple images to find style matches.

**Parameters:**
- `reference_image_path` (required): Path to the reference image
- `comparison_image_paths` (required): Array of paths to images to compare
- `threshold` (optional): Similarity threshold (0-1), default: 0.70

**Example:**
```
Find all images with similar style to reference.jpg from this collection:
- artwork1.jpg
- artwork2.jpg
- artwork3.jpg
```

## How to Use

### With Claude Code

Once configured, simply ask Claude Code to use the image comparison tools naturally:

```
"Compare test_images/character1_blue.jpg and test_images/character1_red.jpg
to see if they show the same character"
```

Claude Code will automatically:
1. Recognize this as an image comparison task
2. Use the `compare_characters` tool
3. Pass the file paths to the MCP server
4. Return the results to you

### Testing the MCP Server

You can test if the MCP server is working by:

1. Checking Claude Code's available tools (the ai-artist tools should appear)
2. Asking Claude Code to compare test images:
   ```
   "Compare test_images/character1_blue.jpg and test_images/character1_red.jpg"
   ```

## Troubleshooting

### Server Won't Start

**Check Python path:**
```bash
which python
# Use the full path in your configuration
```

**Check if dependencies are installed:**
```bash
python -c "import mcp; print('MCP installed')"
python -c "from app.services.clip_service import CLIPService; print('Services OK')"
```

### CLIP Model Not Loading

The first time the server starts, it will download the CLIP model (~350MB). This may take a few minutes. Check the logs to see if the download is in progress.

**Clear cache if needed:**
```bash
rm -rf ~/.cache/torch/sentence_transformers/
```

### Image File Not Found

Make sure to use **absolute paths** to image files, not relative paths. The MCP server runs in a different working directory than your current shell.

**Good:**
```
/Users/username/images/photo.jpg
```

**Bad:**
```
./images/photo.jpg  # This won't work!
```

### Permission Errors

Make sure the Python script has execute permissions:
```bash
chmod +x mcp_server.py
```

## Performance Notes

- **First request**: May take 1-2 seconds as the CLIP model loads into memory
- **Subsequent requests**: Typically 100-500ms per comparison
- **Memory usage**: ~1-2GB for the CLIP model (loaded once when server starts)
- **Batch operations**: More efficient than multiple individual comparisons

## Differences from REST API

| Feature | MCP Server | REST API |
|---------|-----------|----------|
| **Access** | Direct from Claude Code | HTTP requests from any client |
| **Setup** | Add to Claude config | Run server process |
| **Performance** | Slightly faster (no HTTP overhead) | Standard HTTP latency |
| **Use Case** | Claude Code integration | General purpose API |
| **Authentication** | Not needed | Would need to add for production |

You can run **both** the MCP server and REST API simultaneously - they use the same underlying code.

## Advanced Configuration

### Custom Environment Variables

You can pass environment variables to the MCP server via the config:

```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "env": {
        "CHARACTER_SIMILARITY_THRESHOLD": "0.80",
        "STYLE_SIMILARITY_THRESHOLD": "0.75",
        "MAX_IMAGE_SIZE_MB": "15"
      }
    }
  }
}
```

### Using Virtual Environment

If you use a virtual environment:

```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/mcp_server.py"],
      "env": {}
    }
  }
}
```

## Next Steps

- Try the tools with your own images
- Adjust thresholds for your use case
- Integrate with Claude Code workflows
- Explore batch comparison for large collections
