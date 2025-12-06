#!/usr/bin/env python3
"""
Image Generation using Replicate API

Supports multiple models:
- SDXL: Fast, good quality, cheap (~$0.002/image)
- Flux Dev: Better quality, moderate cost (~$0.003/image)
- Flux Pro: Best quality, higher cost (~$0.055/image)
"""

import os
import sys
import json
import urllib.request
import urllib.error
import time
from datetime import datetime
from pathlib import Path


# Model configurations
MODELS = {
    "sdxl": {
        "version": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
        "cost_per_image": 0.002,
    },
    "flux-dev": {
        "version": "black-forest-labs/flux-dev",
        "cost_per_image": 0.003,
    },
    "flux-pro": {
        "version": "black-forest-labs/flux-pro",
        "cost_per_image": 0.055,
    },
    "flux-schnell": {
        "version": "black-forest-labs/flux-schnell",
        "cost_per_image": 0.003,
    },
}


def get_api_token():
    """Get Replicate API token from environment"""
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN environment variable not set")
        print("\nTo set up:")
        print("1. Get a token at: https://replicate.com/account/api-tokens")
        print("2. Run: export REPLICATE_API_TOKEN='r8_your_token_here'")
        print("   Or add to ~/.zshrc for persistence")
        sys.exit(1)
    return token


def make_request(url, data=None, method="GET"):
    """Make HTTP request to Replicate API"""
    token = get_api_token()

    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }

    if data:
        data = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error ({e.code}): {error_body}")
        sys.exit(1)


def generate_image(
    prompt: str,
    model: str = "sdxl",
    output_path: str = None,
    width: int = 1024,
    height: int = 1024,
    negative_prompt: str = "blurry, bad quality, distorted, ugly",
) -> str:
    """
    Generate an image using Replicate API.

    Args:
        prompt: Text description of the image
        model: Model to use (sdxl, flux-dev, flux-pro, flux-schnell)
        output_path: Where to save the image (auto-generated if None)
        width: Image width
        height: Image height
        negative_prompt: What to avoid in the image

    Returns:
        Path to the generated image
    """
    if model not in MODELS:
        print(f"Unknown model: {model}")
        print(f"Available models: {', '.join(MODELS.keys())}")
        sys.exit(1)

    model_config = MODELS[model]

    print(f"Generating image with {model}...")
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"Estimated cost: ${model_config['cost_per_image']:.3f}")

    # Create prediction
    if model.startswith("flux"):
        # Flux models use different API
        input_data = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_outputs": 1,
        }
    else:
        # SDXL
        input_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_outputs": 1,
        }

    # Start prediction
    response = make_request(
        "https://api.replicate.com/v1/predictions",
        data={
            "version": model_config["version"],
            "input": input_data,
        },
        method="POST"
    )

    prediction_id = response["id"]
    print(f"Prediction started: {prediction_id}")

    # Poll for completion
    while True:
        status_response = make_request(
            f"https://api.replicate.com/v1/predictions/{prediction_id}"
        )
        status = status_response["status"]

        if status == "succeeded":
            output = status_response["output"]
            if isinstance(output, list):
                image_url = output[0]
            else:
                image_url = output
            break
        elif status == "failed":
            print(f"Generation failed: {status_response.get('error', 'Unknown error')}")
            sys.exit(1)
        elif status == "canceled":
            print("Generation was canceled")
            sys.exit(1)
        else:
            print(f"Status: {status}...")
            time.sleep(2)

    # Download image
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"generated_{model}_{timestamp}.png"

    print(f"Downloading image to: {output_path}")
    urllib.request.urlretrieve(image_url, output_path)

    print(f"✓ Image saved: {output_path}")
    return output_path


def generate_character_variations(
    prompt: str,
    count: int = 4,
    model: str = "sdxl",
    output_dir: str = None,
) -> list:
    """
    Generate multiple variations of a character.

    Args:
        prompt: Character description
        count: Number of variations to generate
        model: Model to use
        output_dir: Directory to save images (auto-generated if None)

    Returns:
        List of paths to generated images
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"character_variations_{timestamp}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} character variations...")
    print(f"Model: {model}")
    print(f"Output directory: {output_dir}")
    print(f"Estimated total cost: ${MODELS[model]['cost_per_image'] * count:.3f}")
    print()

    generated_paths = []

    for i in range(count):
        print(f"\n--- Variation {i+1}/{count} ---")
        output_path = f"{output_dir}/variation_{i+1:02d}.png"

        path = generate_image(
            prompt=prompt,
            model=model,
            output_path=output_path,
        )
        generated_paths.append(path)

    print(f"\n✓ Generated {count} variations in: {output_dir}")
    print("\nTo compare consistency, use the ai-artist MCP server:")
    print(f"  'Compare all images in {output_dir} for character consistency'")

    return generated_paths


def main():
    """CLI interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate images using Replicate API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single image generation
    gen_parser = subparsers.add_parser("generate", help="Generate a single image")
    gen_parser.add_argument("prompt", help="Text prompt for the image")
    gen_parser.add_argument("--model", default="sdxl", choices=MODELS.keys())
    gen_parser.add_argument("--output", help="Output file path")
    gen_parser.add_argument("--width", type=int, default=1024)
    gen_parser.add_argument("--height", type=int, default=1024)

    # Character variations
    var_parser = subparsers.add_parser("variations", help="Generate character variations")
    var_parser.add_argument("prompt", help="Character description")
    var_parser.add_argument("--count", type=int, default=4)
    var_parser.add_argument("--model", default="sdxl", choices=MODELS.keys())
    var_parser.add_argument("--output-dir", help="Output directory")

    # List models
    subparsers.add_parser("models", help="List available models")

    args = parser.parse_args()

    if args.command == "generate":
        generate_image(
            prompt=args.prompt,
            model=args.model,
            output_path=args.output,
            width=args.width,
            height=args.height,
        )
    elif args.command == "variations":
        generate_character_variations(
            prompt=args.prompt,
            count=args.count,
            model=args.model,
            output_dir=args.output_dir,
        )
    elif args.command == "models":
        print("Available models:")
        for name, config in MODELS.items():
            print(f"  {name}: ~${config['cost_per_image']:.3f}/image")


if __name__ == "__main__":
    main()
