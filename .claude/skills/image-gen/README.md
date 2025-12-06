# Image Generation Skill

Generate images using Replicate API with Stable Diffusion, Flux, and other models.

## Quick Start

### 1. Get API Token (Free to Start)

1. Go to https://replicate.com
2. Sign up (free)
3. Go to https://replicate.com/account/api-tokens
4. Create a new token

### 2. Set Environment Variable

**Temporary (current session):**
```bash
export REPLICATE_API_TOKEN="r8_your_token_here"
```

**Permanent (recommended):**
```bash
echo 'export REPLICATE_API_TOKEN="r8_your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Use in Claude Code

Just ask Claude Code to generate images:

```
"Generate an image of a blue-haired warrior character in anime style"

"Generate 5 variations of a red-haired elven mage for character consistency testing"
```

## Available Models

| Model | Quality | Speed | Cost/Image |
|-------|---------|-------|------------|
| `sdxl` | ⭐⭐⭐⭐ Good | Fast | $0.002 |
| `flux-schnell` | ⭐⭐⭐⭐ Good | Very Fast | $0.003 |
| `flux-dev` | ⭐⭐⭐⭐⭐ Excellent | Medium | $0.003 |
| `flux-pro` | ⭐⭐⭐⭐⭐ Best | Medium | $0.055 |

**Default:** `sdxl` (best value for experimentation)

## CLI Usage

You can also use the script directly:

```bash
# Generate single image
python generate.py generate "a blue-haired warrior in anime style"

# Generate with specific model
python generate.py generate "a forest background" --model flux-dev

# Generate character variations
python generate.py variations "a red-haired elven mage" --count 5

# List available models
python generate.py models
```

## Workflow: Character Consistency

1. **Generate variations:**
   ```
   "Generate 6 variations of my character: a young woman with
   purple hair, green eyes, wearing a black leather jacket"
   ```

2. **Compare with MCP server:**
   ```
   "Compare all the generated images to find the most consistent ones"
   ```

3. **Keep the best matches:**
   ```
   "Which images have similarity > 0.8?"
   ```

4. **Iterate:**
   ```
   "Generate 4 more variations similar to variation_03.png"
   ```

## Cost Examples

| Usage | Model | Monthly Cost |
|-------|-------|--------------|
| 50 images | SDXL | $0.10 |
| 100 images | SDXL | $0.20 |
| 50 images | Flux Pro | $2.75 |
| 100 images | Flux Pro | $5.50 |

## Files

- `generate.py` - Main generation script
- `skill.md` - Skill definition for Claude Code
- `README.md` - This file

## Troubleshooting

### "REPLICATE_API_TOKEN not set"
```bash
export REPLICATE_API_TOKEN="r8_your_token_here"
```

### "API Error (401)"
Your token is invalid. Get a new one at https://replicate.com/account/api-tokens

### "API Error (402)"
You need to add billing info to Replicate (even for free tier).

### Slow generation
- SDXL: 10-30 seconds
- Flux models: 30-60 seconds
This is normal for API-based generation.

## Integration with AI Artist MCP

This skill works seamlessly with your AI Artist MCP server:

1. **Generate** images with this skill
2. **Compare** them with the MCP server's `compare_characters` or `compare_styles` tools
3. **Filter** to keep only consistent images

The MCP server is always ready for fast comparisons (~200ms each).
