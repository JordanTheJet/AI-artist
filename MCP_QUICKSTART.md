# MCP Server Quick Start

Get the AI Artist MCP server running with Claude Code in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Claude Code installed
- This repository cloned

## Step 1: Install Dependencies (2 minutes)

```bash
cd AI-artist
pip install -r requirements.txt
```

**Note**: First install downloads the CLIP model (~350MB). This may take a few minutes.

## Step 2: Get the Absolute Path (30 seconds)

```bash
pwd
# Example output: /Users/yourname/Documents/AI-artist
```

Copy this path. You'll need it in the next step.

## Step 3: Configure Claude Code (1 minute)

1. Open your Claude Code configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add this configuration (replace `/path/to/AI-artist` with your actual path from Step 2):

```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "python",
      "args": [
        "/path/to/AI-artist/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "python",
      "args": [
        "/Users/john/Documents/AI-artist/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

**Windows Example:**
```json
{
  "mcpServers": {
    "ai-artist": {
      "command": "python",
      "args": [
        "C:\\Users\\john\\Documents\\AI-artist\\mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

3. Save the file

## Step 4: Restart Claude Code (30 seconds)

Completely quit and restart Claude Code for the changes to take effect.

## Step 5: Test It! (1 minute)

Open Claude Code and try this:

```
Compare these two test images to see if they show the same character:
- /absolute/path/to/AI-artist/test_images/character1_blue.jpg
- /absolute/path/to/AI-artist/test_images/character1_red.jpg
```

**Remember**: Use absolute paths! Replace `/absolute/path/to/AI-artist` with your actual path.

## What to Expect

Claude Code will:
1. Recognize this as an image comparison task
2. Use the `compare_characters` tool from your MCP server
3. Load the CLIP model (first time only, ~2 seconds)
4. Analyze the images
5. Return results like:

```
Character Comparison Result:

Match: True
Similarity Score: 89.23%
Confidence: high
Method: CLIP + Perceptual Hashing

The images likely show the same character (similarity: 89.23%)
```

## Common Issues

### "Module 'mcp' not found"
```bash
pip install mcp>=1.0.0
```

### "File not found" errors
Make sure you're using **absolute paths**, not relative paths:
- ✅ Good: `/Users/john/images/photo.jpg`
- ❌ Bad: `./images/photo.jpg`

### Server won't start
Check your Python path:
```bash
which python
# Use this full path in the config instead of just "python"
```

### Need more help?
See `MCP_SETUP.md` for detailed troubleshooting.

## Next Steps

Try these commands with Claude Code:

1. **Character comparison:**
   ```
   "Are these two images of the same character?
   image1.jpg and image2.jpg"
   ```

2. **Style comparison:**
   ```
   "Do these images have similar artistic styles?
   artwork1.jpg and artwork2.jpg"
   ```

3. **Batch comparison:**
   ```
   "Find all images in this folder that show the same character as reference.jpg:
   - image1.jpg
   - image2.jpg
   - image3.jpg"
   ```

## What's Available

Four tools are now available in Claude Code:
- `compare_characters` - Character matching
- `compare_styles` - Style matching
- `batch_compare_characters` - Batch character matching
- `batch_compare_styles` - Batch style matching

Just ask Claude Code naturally - it will figure out which tool to use!

## Performance Tips

- **First comparison**: Takes 1-2 seconds (loads CLIP model)
- **After that**: 100-500ms per comparison
- **Batch operations**: Faster than individual comparisons
- **Memory**: Uses ~1-2GB RAM (loaded once, reused for all comparisons)

## Documentation

- **Full setup guide**: `MCP_SETUP.md`
- **Architecture details**: `CLAUDE.md`
- **Implementation summary**: `MCP_SUMMARY.md`
- **REST API docs**: `README.md`
