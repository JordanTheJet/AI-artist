"""
MCP Server for AI Artist Image Comparison

This MCP server exposes the image comparison functionality to Claude Code
and other MCP-compatible clients.
"""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from app.services.character_comparison import CharacterComparison
from app.services.style_comparison import StyleComparison
from app.services.clip_service import CLIPService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai-artist-mcp")

# Initialize services
character_service = CharacterComparison()
style_service = StyleComparison()
clip_service = CLIPService()

# Create MCP server
app = Server("ai-artist")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="compare_characters",
            description="""Compare two images to determine if they show the same character.

This tool uses AI (CLIP) and perceptual hashing to analyze if two images show the same character,
even if they're in different poses, angles, colors, or contexts.

Returns:
- is_match: Whether the images show the same character
- similarity_score: Score from 0.0 to 1.0
- confidence: Confidence level (low, medium, high)
- message: Human-readable description""",
            inputSchema={
                "type": "object",
                "properties": {
                    "image1_path": {
                        "type": "string",
                        "description": "Path to the first image file"
                    },
                    "image2_path": {
                        "type": "string",
                        "description": "Path to the second image file"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0-1). Default: 0.75",
                        "default": 0.75,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["image1_path", "image2_path"]
            }
        ),
        Tool(
            name="compare_styles",
            description="""Compare two images to determine if they have the same visual/artistic style.

This tool analyzes color palettes, brightness, saturation, and semantic features to determine
if two images share the same artistic or visual style.

Returns:
- is_match: Whether the images have matching styles
- similarity_score: Score from 0.0 to 1.0
- confidence: Confidence level (low, medium, high)
- style_features: Detailed breakdown (color_similarity, brightness_similarity, etc.)
- message: Human-readable description""",
            inputSchema={
                "type": "object",
                "properties": {
                    "image1_path": {
                        "type": "string",
                        "description": "Path to the first image file"
                    },
                    "image2_path": {
                        "type": "string",
                        "description": "Path to the second image file"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0-1). Default: 0.70",
                        "default": 0.70,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["image1_path", "image2_path"]
            }
        ),
        Tool(
            name="batch_compare_characters",
            description="""Compare one reference image with multiple images to find character matches.

This is useful for finding which images in a collection show the same character as a reference image.

Returns:
- total_images: Number of images compared
- matches: List of matching images with their scores
- best_match: The best matching image (if any)
- message: Summary of results""",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference_image_path": {
                        "type": "string",
                        "description": "Path to the reference image file"
                    },
                    "comparison_image_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paths to images to compare against reference"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0-1). Default: 0.75",
                        "default": 0.75,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["reference_image_path", "comparison_image_paths"]
            }
        ),
        Tool(
            name="batch_compare_styles",
            description="""Compare one reference image with multiple images to find style matches.

This is useful for finding which images in a collection have the same visual/artistic style
as a reference image.

Returns:
- total_images: Number of images compared
- matches: List of matching images with their scores
- best_match: The best matching image (if any)
- message: Summary of results""",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference_image_path": {
                        "type": "string",
                        "description": "Path to the reference image file"
                    },
                    "comparison_image_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paths to images to compare against reference"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Similarity threshold (0-1). Default: 0.70",
                        "default": 0.70,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["reference_image_path", "comparison_image_paths"]
            }
        ),
    ]


def read_image_file(file_path: str) -> bytes:
    """Read image file and return bytes"""
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Image file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading image file {file_path}: {str(e)}")


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "compare_characters":
            # Read images
            image1_bytes = read_image_file(arguments["image1_path"])
            image2_bytes = read_image_file(arguments["image2_path"])
            threshold = arguments.get("threshold", 0.75)

            # Perform comparison
            is_match, similarity, confidence = character_service.compare_characters(
                image1_bytes, image2_bytes, threshold=threshold
            )

            # Build result message
            result = {
                "is_match": is_match,
                "similarity_score": round(similarity, 4),
                "confidence": confidence,
                "method": "CLIP + Perceptual Hashing",
            }

            if is_match:
                result["message"] = f"The images likely show the same character (similarity: {similarity:.2%})"
            else:
                result["message"] = f"The images likely show different characters (similarity: {similarity:.2%})"

            return [TextContent(
                type="text",
                text=f"Character Comparison Result:\n\n" +
                     f"Match: {result['is_match']}\n" +
                     f"Similarity Score: {result['similarity_score']:.2%}\n" +
                     f"Confidence: {result['confidence']}\n" +
                     f"Method: {result['method']}\n\n" +
                     f"{result['message']}"
            )]

        elif name == "compare_styles":
            # Read images
            image1_bytes = read_image_file(arguments["image1_path"])
            image2_bytes = read_image_file(arguments["image2_path"])
            threshold = arguments.get("threshold", 0.70)

            # Perform comparison
            is_match, similarity, confidence, style_features = style_service.compare_styles(
                image1_bytes, image2_bytes, threshold=threshold
            )

            # Build result message
            result = {
                "is_match": is_match,
                "similarity_score": round(similarity, 4),
                "confidence": confidence,
                "method": "CLIP + Color Analysis + Style Features",
                "style_features": style_features,
            }

            if is_match:
                result["message"] = f"The images have similar visual styles (similarity: {similarity:.2%})"
            else:
                result["message"] = f"The images have different visual styles (similarity: {similarity:.2%})"

            style_breakdown = "\n".join([
                f"  - {k.replace('_', ' ').title()}: {v:.2%}"
                for k, v in style_features.items()
            ])

            return [TextContent(
                type="text",
                text=f"Style Comparison Result:\n\n" +
                     f"Match: {result['is_match']}\n" +
                     f"Similarity Score: {result['similarity_score']:.2%}\n" +
                     f"Confidence: {result['confidence']}\n" +
                     f"Method: {result['method']}\n\n" +
                     f"Style Features:\n{style_breakdown}\n\n" +
                     f"{result['message']}"
            )]

        elif name == "batch_compare_characters":
            # Read reference image
            ref_bytes = read_image_file(arguments["reference_image_path"])
            threshold = arguments.get("threshold", 0.75)

            # Read comparison images
            comp_bytes_list = []
            for path in arguments["comparison_image_paths"]:
                comp_bytes_list.append(read_image_file(path))

            # Perform batch comparison
            results = character_service.compare_character_batch(
                ref_bytes, comp_bytes_list, threshold=threshold
            )

            # Build response
            matches = []
            for idx, similarity, is_match in results:
                if is_match:
                    matches.append({
                        "image_index": idx,
                        "image_path": arguments["comparison_image_paths"][idx],
                        "similarity_score": round(similarity, 4),
                        "is_match": True
                    })

            best_match = None
            if results:
                best_idx, best_sim, best_is_match = results[0]
                best_match = {
                    "image_index": best_idx,
                    "image_path": arguments["comparison_image_paths"][best_idx],
                    "similarity_score": round(best_sim, 4),
                    "is_match": best_is_match
                }

            # Format output
            output_lines = [
                "Batch Character Comparison Result:",
                "",
                f"Total Images: {len(comp_bytes_list)}",
                f"Matches Found: {len(matches)}",
                ""
            ]

            if best_match:
                output_lines.extend([
                    "Best Match:",
                    f"  - Image: {best_match['image_path']}",
                    f"  - Index: {best_match['image_index']}",
                    f"  - Similarity: {best_match['similarity_score']:.2%}",
                    f"  - Is Match: {best_match['is_match']}",
                    ""
                ])

            if matches:
                output_lines.append("All Matches:")
                for match in matches:
                    output_lines.append(
                        f"  - Image {match['image_index']} ({match['image_path']}): {match['similarity_score']:.2%}"
                    )
                output_lines.append("")
                output_lines.append(f"Found {len(matches)} matching image(s) out of {len(comp_bytes_list)}")
            else:
                output_lines.append(f"No matching characters found in {len(comp_bytes_list)} images")

            return [TextContent(type="text", text="\n".join(output_lines))]

        elif name == "batch_compare_styles":
            # Read reference image
            ref_bytes = read_image_file(arguments["reference_image_path"])
            threshold = arguments.get("threshold", 0.70)

            # Read comparison images
            comp_bytes_list = []
            for path in arguments["comparison_image_paths"]:
                comp_bytes_list.append(read_image_file(path))

            # Perform batch comparison
            results = style_service.compare_style_batch(
                ref_bytes, comp_bytes_list, threshold=threshold
            )

            # Build response
            matches = []
            for idx, similarity, is_match in results:
                if is_match:
                    matches.append({
                        "image_index": idx,
                        "image_path": arguments["comparison_image_paths"][idx],
                        "similarity_score": round(similarity, 4),
                        "is_match": True
                    })

            best_match = None
            if results:
                best_idx, best_sim, best_is_match = results[0]
                best_match = {
                    "image_index": best_idx,
                    "image_path": arguments["comparison_image_paths"][best_idx],
                    "similarity_score": round(best_sim, 4),
                    "is_match": best_is_match
                }

            # Format output
            output_lines = [
                "Batch Style Comparison Result:",
                "",
                f"Total Images: {len(comp_bytes_list)}",
                f"Matches Found: {len(matches)}",
                ""
            ]

            if best_match:
                output_lines.extend([
                    "Best Match:",
                    f"  - Image: {best_match['image_path']}",
                    f"  - Index: {best_match['image_index']}",
                    f"  - Similarity: {best_match['similarity_score']:.2%}",
                    f"  - Is Match: {best_match['is_match']}",
                    ""
                ])

            if matches:
                output_lines.append("All Matches:")
                for match in matches:
                    output_lines.append(
                        f"  - Image {match['image_index']} ({match['image_path']}): {match['similarity_score']:.2%}"
                    )
                output_lines.append("")
                output_lines.append(f"Found {len(matches)} image(s) with matching style out of {len(comp_bytes_list)}")
            else:
                output_lines.append(f"No matching styles found in {len(comp_bytes_list)} images")

            return [TextContent(type="text", text="\n".join(output_lines))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    logger.info("Starting AI Artist MCP Server...")

    # Preload CLIP model
    try:
        logger.info("Loading CLIP model...")
        _ = CLIPService()
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load CLIP model: {e}")
        logger.warning("Server will start but comparisons may fail")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("MCP Server ready")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
