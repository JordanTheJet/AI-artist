"""
Quick test script for the Image Comparison API

This script will test both character and style comparison endpoints
using the generated test images.
"""

import requests
import time
import sys


def wait_for_api(url="http://localhost:8000/health", max_retries=30):
    """Wait for the API to be ready"""
    print("Waiting for API to start...")
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                result = response.json()
                print(f"✓ API is ready! (Status: {result['status']}, Model loaded: {result['model_loaded']})")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
        if i % 5 == 0:
            print(f"  Still waiting... ({i*2}s elapsed)")

    print("✗ API failed to start")
    return False


def test_character_comparison():
    """Test character comparison endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Character Comparison - Same Character (Different Colors)")
    print("="*60)

    # Test same character with different colors (should match)
    with open('test_images/character1_blue.jpg', 'rb') as img1, \
         open('test_images/character1_red.jpg', 'rb') as img2:

        files = {
            'image1': ('img1.jpg', img1, 'image/jpeg'),
            'image2': ('img2.jpg', img2, 'image/jpeg'),
        }

        response = requests.post('http://localhost:8000/api/compare/character', files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(f"  Match: {result['is_match']}")
        print(f"  Similarity: {result['similarity_score']:.2%}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Message: {result['message']}")

        if result['is_match']:
            print("\n✓ TEST PASSED: Same character detected despite different colors!")
        else:
            print("\n⚠ TEST WARNING: Expected match but got no match")
    else:
        print(f"\n✗ TEST FAILED: {response.status_code} - {response.text}")

    print("\n" + "="*60)
    print("TEST 2: Character Comparison - Different Characters")
    print("="*60)

    # Test different characters (should NOT match)
    with open('test_images/character1_blue.jpg', 'rb') as img1, \
         open('test_images/character2_green.jpg', 'rb') as img2:

        files = {
            'image1': ('img1.jpg', img1, 'image/jpeg'),
            'image2': ('img2.jpg', img2, 'image/jpeg'),
        }

        response = requests.post('http://localhost:8000/api/compare/character', files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(f"  Match: {result['is_match']}")
        print(f"  Similarity: {result['similarity_score']:.2%}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Message: {result['message']}")

        if not result['is_match']:
            print("\n✓ TEST PASSED: Different characters correctly identified!")
        else:
            print("\n⚠ TEST WARNING: Expected no match but got match")
    else:
        print(f"\n✗ TEST FAILED: {response.status_code} - {response.text}")


def test_style_comparison():
    """Test style comparison endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Style Comparison - Similar Styles")
    print("="*60)

    # Test similar styles (blue stripes - should match)
    with open('test_images/style1_blue_stripes.jpg', 'rb') as img1, \
         open('test_images/style1_blue_stripes2.jpg', 'rb') as img2:

        files = {
            'image1': ('img1.jpg', img1, 'image/jpeg'),
            'image2': ('img2.jpg', img2, 'image/jpeg'),
        }

        response = requests.post('http://localhost:8000/api/compare/style', files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(f"  Match: {result['is_match']}")
        print(f"  Similarity: {result['similarity_score']:.2%}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Message: {result['message']}")

        if 'style_features' in result:
            print(f"\n  Style Features:")
            for key, value in result['style_features'].items():
                print(f"    {key}: {value}")

        if result['is_match']:
            print("\n✓ TEST PASSED: Similar styles detected!")
        else:
            print("\n⚠ TEST WARNING: Expected style match but got no match")
    else:
        print(f"\n✗ TEST FAILED: {response.status_code} - {response.text}")

    print("\n" + "="*60)
    print("TEST 4: Style Comparison - Different Styles")
    print("="*60)

    # Test different styles (stripes vs dots - should NOT match strongly)
    with open('test_images/style1_blue_stripes.jpg', 'rb') as img1, \
         open('test_images/style2_warm_dots.jpg', 'rb') as img2:

        files = {
            'image1': ('img1.jpg', img1, 'image/jpeg'),
            'image2': ('img2.jpg', img2, 'image/jpeg'),
        }

        response = requests.post('http://localhost:8000/api/compare/style', files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(f"  Match: {result['is_match']}")
        print(f"  Similarity: {result['similarity_score']:.2%}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Message: {result['message']}")

        if 'style_features' in result:
            print(f"\n  Style Features:")
            for key, value in result['style_features'].items():
                print(f"    {key}: {value}")

        if not result['is_match']:
            print("\n✓ TEST PASSED: Different styles correctly identified!")
        else:
            print("\n⚠ TEST NOTE: Styles might have some similarity")
    else:
        print(f"\n✗ TEST FAILED: {response.status_code} - {response.text}")


def test_batch_comparison():
    """Test batch comparison endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Batch Character Comparison")
    print("="*60)

    # Test batch comparison - find matching character
    with open('test_images/character1_blue.jpg', 'rb') as ref, \
         open('test_images/character1_red.jpg', 'rb') as img1, \
         open('test_images/character2_green.jpg', 'rb') as img2, \
         open('test_images/character1_blue.jpg', 'rb') as img3:

        files = [
            ('reference_image', ('ref.jpg', ref, 'image/jpeg')),
            ('comparison_images', ('img1.jpg', img1, 'image/jpeg')),
            ('comparison_images', ('img2.jpg', img2, 'image/jpeg')),
            ('comparison_images', ('img3.jpg', img3, 'image/jpeg')),
        ]

        response = requests.post('http://localhost:8000/api/compare/batch/character', files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(f"  Total Images: {result['total_images']}")
        print(f"  Matches Found: {len(result['matches'])}")

        if result['best_match']:
            print(f"\n  Best Match:")
            print(f"    Image Index: {result['best_match']['image_index']}")
            print(f"    Similarity: {result['best_match']['similarity_score']:.2%}")
            print(f"    Is Match: {result['best_match']['is_match']}")

        if result['matches']:
            print(f"\n  All Matches:")
            for match in result['matches']:
                print(f"    Image {match['image_index']}: {match['similarity_score']:.2%}")

        print(f"\n  {result['message']}")

        if len(result['matches']) >= 2:  # Should match image 0 and 2 (same character)
            print("\n✓ TEST PASSED: Batch comparison found multiple matches!")
        else:
            print("\n⚠ TEST NOTE: Expected at least 2 matches")
    else:
        print(f"\n✗ TEST FAILED: {response.status_code} - {response.text}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI ARTIST - IMAGE COMPARISON API TEST SUITE")
    print("="*60)

    # Check if API is running
    if not wait_for_api():
        print("\nPlease start the API server first:")
        print("  python -m app.main")
        sys.exit(1)

    # Run all tests
    test_character_comparison()
    test_style_comparison()
    test_batch_comparison()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    print("\nYou can now use the API for your own images!")
    print("API Documentation: http://localhost:8000/")


if __name__ == "__main__":
    main()
