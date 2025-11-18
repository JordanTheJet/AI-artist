"""
Example script demonstrating how to use the AI Artist Image Comparison API
"""

import requests
import sys


def compare_characters(image1_path: str, image2_path: str, api_url: str = "http://localhost:8000"):
    """
    Compare two images for character similarity

    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        api_url: Base URL of the API (default: http://localhost:8000)
    """
    endpoint = f"{api_url}/api/compare/character"

    # Open the image files
    with open(image1_path, "rb") as img1, open(image2_path, "rb") as img2:
        files = {
            "image1": ("image1.jpg", img1, "image/jpeg"),
            "image2": ("image2.jpg", img2, "image/jpeg"),
        }

        # Make the request
        response = requests.post(endpoint, files=files)

    if response.status_code == 200:
        result = response.json()
        print("\n=== Character Comparison Result ===")
        print(f"Match: {result['is_match']}")
        print(f"Similarity: {result['similarity_score']:.2%}")
        print(f"Confidence: {result['confidence']}")
        print(f"Message: {result['message']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None


def compare_styles(image1_path: str, image2_path: str, api_url: str = "http://localhost:8000"):
    """
    Compare two images for style similarity

    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        api_url: Base URL of the API (default: http://localhost:8000)
    """
    endpoint = f"{api_url}/api/compare/style"

    with open(image1_path, "rb") as img1, open(image2_path, "rb") as img2:
        files = {
            "image1": ("image1.jpg", img1, "image/jpeg"),
            "image2": ("image2.jpg", img2, "image/jpeg"),
        }

        response = requests.post(endpoint, files=files)

    if response.status_code == 200:
        result = response.json()
        print("\n=== Style Comparison Result ===")
        print(f"Match: {result['is_match']}")
        print(f"Similarity: {result['similarity_score']:.2%}")
        print(f"Confidence: {result['confidence']}")
        print(f"Message: {result['message']}")
        if "style_features" in result:
            print("\nStyle Features:")
            for key, value in result["style_features"].items():
                print(f"  {key}: {value}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None


def batch_compare_characters(
    reference_path: str, image_paths: list, api_url: str = "http://localhost:8000"
):
    """
    Compare one reference image with multiple images for character matching

    Args:
        reference_path: Path to reference image
        image_paths: List of paths to comparison images
        api_url: Base URL of the API (default: http://localhost:8000)
    """
    endpoint = f"{api_url}/api/compare/batch/character"

    # Build files dict
    files = [("reference_image", ("reference.jpg", open(reference_path, "rb"), "image/jpeg"))]

    # Add all comparison images
    comparison_files = []
    for img_path in image_paths:
        comparison_files.append(
            ("comparison_images", (img_path, open(img_path, "rb"), "image/jpeg"))
        )
    files.extend(comparison_files)

    response = requests.post(endpoint, files=files)

    # Close all files
    for _, (_, f, _) in files:
        f.close()

    if response.status_code == 200:
        result = response.json()
        print("\n=== Batch Character Comparison Result ===")
        print(f"Total Images: {result['total_images']}")
        print(f"Matches Found: {len(result['matches'])}")

        if result["best_match"]:
            print(f"\nBest Match:")
            print(f"  Index: {result['best_match']['image_index']}")
            print(f"  Similarity: {result['best_match']['similarity_score']:.2%}")

        if result["matches"]:
            print("\nAll Matches:")
            for match in result["matches"]:
                print(f"  Image {match['image_index']}: {match['similarity_score']:.2%}")

        print(f"\n{result['message']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None


def check_health(api_url: str = "http://localhost:8000"):
    """
    Check API health status

    Args:
        api_url: Base URL of the API (default: http://localhost:8000)
    """
    endpoint = f"{api_url}/health"

    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            result = response.json()
            print("\n=== API Health Status ===")
            print(f"Status: {result['status']}")
            print(f"Version: {result['version']}")
            print(f"Model Loaded: {result['model_loaded']}")
            return result
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running.")
        return None


if __name__ == "__main__":
    # Example usage
    print("AI Artist - Image Comparison API Client")
    print("========================================")

    # Check if API is running
    if not check_health():
        print("\nPlease start the API server first:")
        print("  python -m app.main")
        sys.exit(1)

    print("\nAPI is running!")
    print("\nTo use this client, provide image paths:")
    print("\nExample:")
    print("  python example_usage.py")
    print("\nThen uncomment and modify the example calls below:\n")

    # Uncomment these examples and replace with your image paths:

    # Example 1: Character comparison
    # compare_characters("path/to/image1.jpg", "path/to/image2.jpg")

    # Example 2: Style comparison
    # compare_styles("path/to/style1.jpg", "path/to/style2.jpg")

    # Example 3: Batch character comparison
    # batch_compare_characters(
    #     "path/to/reference.jpg",
    #     ["path/to/img1.jpg", "path/to/img2.jpg", "path/to/img3.jpg"]
    # )
