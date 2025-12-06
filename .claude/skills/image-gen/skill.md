# Image Generation Skill

Generate images using Replicate API (Stable Diffusion, Flux, SDXL).

## Setup Required

1. Get a Replicate API token: https://replicate.com/account/api-tokens
2. Set the environment variable:
   ```bash
   export REPLICATE_API_TOKEN="r8_your_token_here"
   ```
   Or add to your shell profile (~/.zshrc):
   ```bash
   echo 'export REPLICATE_API_TOKEN="r8_your_token_here"' >> ~/.zshrc
   source ~/.zshrc
   ```

## Available Functions

### generate_image
Generate an image from a text prompt.

**Parameters:**
- `prompt` (required): Text description of the image to generate
- `model` (optional): Model to use - "sdxl", "flux-dev", "flux-pro" (default: "sdxl")
- `output_path` (optional): Where to save the image (default: auto-generated in current directory)
- `width` (optional): Image width (default: 1024)
- `height` (optional): Image height (default: 1024)

**Example:**
```
Generate an image of a blue-haired warrior character in anime style
```

### generate_character_variations
Generate multiple variations of a character for consistency testing.

**Parameters:**
- `prompt` (required): Character description
- `count` (optional): Number of variations to generate (default: 4)
- `model` (optional): Model to use (default: "sdxl")

**Example:**
```
Generate 5 variations of a red-haired elven mage character
```

## Pricing (Approximate)

- SDXL: ~$0.002 per image
- Flux Dev: ~$0.003 per image
- Flux Pro: ~$0.055 per image (best quality)

## Usage Tips

1. For character consistency work:
   - Generate variations with this skill
   - Compare them using the ai-artist MCP server
   - Keep the most consistent ones

2. For style matching:
   - Generate images with specific style prompts
   - Use compare_styles to verify style consistency
