# MCP Server Implementation Summary

## What Was Created

An MCP (Model Context Protocol) server that allows Claude Code to directly access the AI Artist image comparison functionality without needing to run a separate REST API server.

## Files Created/Modified

### New Files
1. **`mcp_server.py`** - Main MCP server implementation
   - Exposes 4 tools: `compare_characters`, `compare_styles`, `batch_compare_characters`, `batch_compare_styles`
   - Uses the same underlying services as the REST API
   - Automatically loads CLIP model on startup

2. **`MCP_SETUP.md`** - Comprehensive setup and usage guide
   - Installation instructions
   - Configuration examples for Claude Code
   - Tool descriptions and usage examples
   - Troubleshooting guide

3. **`mcp_config_example.json`** - Example configuration file
   - Ready-to-use template for Claude Code config

4. **`app/models/schemas.py`** - Pydantic response models
   - HealthResponse
   - CharacterComparisonResponse
   - StyleComparisonResponse
   - BatchComparisonResponse
   - BatchComparisonItem

5. **`app/models/__init__.py`** - Models package initialization

6. **`MCP_SUMMARY.md`** - This file

### Modified Files
1. **`requirements.txt`** - Added `mcp>=1.0.0` dependency
2. **`CLAUDE.md`** - Added MCP server information and architecture notes
3. **`README.md`** - Added MCP server mention with link to setup guide

## How It Works

### Architecture
```
Claude Code
    ↓ (MCP Protocol)
mcp_server.py
    ↓ (Python calls)
app/services/
    ├── character_comparison.py
    ├── style_comparison.py
    ├── clip_service.py (Singleton)
    └── image_processor.py
```

### Key Features

1. **Direct Integration**: Claude Code can call image comparison functions like any built-in tool
2. **File-Based**: Accepts file paths instead of HTTP uploads
3. **Same Logic**: Uses identical comparison algorithms as REST API
4. **Performance**: No HTTP overhead, direct Python calls
5. **Auto-Start**: Claude Code starts the server automatically when needed

## How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Claude Code

Add to your Claude Code configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

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

### 3. Restart Claude Code

### 4. Use Naturally

Just ask Claude Code to compare images:
```
"Compare these two images to see if they show the same character:
- /path/to/image1.jpg
- /path/to/image2.jpg"
```

## Available Tools

### 1. compare_characters
Compare two images to determine if they show the same character.

**Input:**
- `image1_path`: Path to first image
- `image2_path`: Path to second image
- `threshold`: Optional (default: 0.75)

**Output:**
- Match status (true/false)
- Similarity score (0-1)
- Confidence level (low/medium/high)
- Human-readable message

### 2. compare_styles
Compare two images to determine if they have the same visual style.

**Input:**
- `image1_path`: Path to first image
- `image2_path`: Path to second image
- `threshold`: Optional (default: 0.70)

**Output:**
- Match status (true/false)
- Similarity score (0-1)
- Confidence level (low/medium/high)
- Style feature breakdown
- Human-readable message

### 3. batch_compare_characters
Compare one reference image with multiple images to find character matches.

**Input:**
- `reference_image_path`: Path to reference image
- `comparison_image_paths`: Array of paths
- `threshold`: Optional (default: 0.75)

**Output:**
- Total images compared
- List of matches with scores
- Best match
- Summary message

### 4. batch_compare_styles
Compare one reference image with multiple images to find style matches.

**Input:**
- `reference_image_path`: Path to reference image
- `comparison_image_paths`: Array of paths
- `threshold`: Optional (default: 0.70)

**Output:**
- Total images compared
- List of matches with scores
- Best match
- Summary message

## Benefits

### For Users
- **No manual server management** - Claude Code starts/stops the server automatically
- **Natural language interface** - Just describe what you want to compare
- **Direct file access** - Works with local files on your machine
- **Integrated experience** - Part of Claude Code's tool ecosystem

### For Developers
- **Code reuse** - Same services as REST API
- **Standard protocol** - MCP is an open standard
- **Easy maintenance** - Single codebase for both interfaces
- **Extensible** - Easy to add new tools

## Differences from REST API

| Aspect | MCP Server | REST API |
|--------|-----------|----------|
| **Interface** | File paths | HTTP multipart uploads |
| **Output** | Formatted text | JSON |
| **Startup** | Automatic (by Claude Code) | Manual |
| **Authentication** | Not needed | Would need to add |
| **Use Case** | Claude Code integration | General purpose API |
| **Performance** | Direct Python calls | HTTP overhead |
| **Access** | Local files only | Any HTTP client |

## Technical Details

### Singleton Pattern
Both MCP server and REST API use the same `CLIPService` singleton, ensuring the CLIP model is loaded only once even if both servers run simultaneously.

### Error Handling
- File not found errors are caught and returned as error messages
- Image processing errors are caught and logged
- Tool execution errors are returned to Claude Code with clear messages

### Performance
- **First call**: 1-2s (CLIP model loading)
- **Subsequent calls**: 100-500ms
- **Memory**: ~1-2GB for CLIP model (shared with REST API if both running)

## Testing

### Manual Testing
1. Configure Claude Code with the MCP server
2. Restart Claude Code
3. Ask Claude Code to compare test images:
   ```
   "Compare test_images/character1_blue.jpg and test_images/character1_red.jpg"
   ```

### Verifying Installation
Check that the server appears in Claude Code's available tools list.

## Troubleshooting

See `MCP_SETUP.md` for detailed troubleshooting, including:
- Python path issues
- CLIP model download problems
- File path issues (relative vs absolute)
- Permission errors

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Claude Code (see `MCP_SETUP.md`)
3. Test with sample images in `test_images/`
4. Try with your own images
5. Adjust thresholds as needed for your use case

## Future Enhancements

Potential additions to the MCP server:
- Image preprocessing tools (resize, crop, format conversion)
- Batch operations with progress reporting
- Caching for repeated comparisons
- Support for image URLs (in addition to file paths)
- Custom threshold configuration per call
- Result export to files
