#!/usr/bin/env python
"""
Simple test to verify MCP server can be imported and dependencies are available.
Run this to check if your MCP server setup is correct before configuring Claude Code.
"""

import sys

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")

    try:
        print("  ✓ Testing mcp package...")
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
        print("    ✓ MCP package OK")
    except ImportError as e:
        print(f"    ✗ MCP package missing: {e}")
        print("    → Run: pip install mcp>=1.0.0")
        return False

    try:
        print("  ✓ Testing service imports...")
        from app.services.character_comparison import CharacterComparison
        from app.services.style_comparison import StyleComparison
        from app.services.clip_service import CLIPService
        print("    ✓ Service imports OK")
    except ImportError as e:
        print(f"    ✗ Service import failed: {e}")
        print("    → Check that all dependencies are installed: pip install -r requirements.txt")
        return False

    return True


def test_services():
    """Test that services can be instantiated"""
    print("\nTesting service initialization...")

    try:
        print("  ✓ Initializing CLIP service...")
        from app.services.clip_service import CLIPService
        clip_service = CLIPService()

        if clip_service.is_model_loaded():
            print("    ✓ CLIP model loaded successfully")
        else:
            print("    ✗ CLIP model not loaded")
            return False

    except Exception as e:
        print(f"    ✗ CLIP service initialization failed: {e}")
        print("    → This is expected on first run (model will download ~350MB)")
        print("    → Try running the test again after the download completes")
        return False

    try:
        print("  ✓ Initializing comparison services...")
        from app.services.character_comparison import CharacterComparison
        from app.services.style_comparison import StyleComparison

        character_service = CharacterComparison()
        style_service = StyleComparison()
        print("    ✓ Comparison services OK")
    except Exception as e:
        print(f"    ✗ Comparison service initialization failed: {e}")
        return False

    return True


def main():
    print("="*60)
    print("MCP Server Import Test")
    print("="*60)
    print()

    imports_ok = test_imports()
    if not imports_ok:
        print("\n" + "="*60)
        print("RESULT: Import test failed")
        print("="*60)
        sys.exit(1)

    services_ok = test_services()
    if not services_ok:
        print("\n" + "="*60)
        print("RESULT: Service initialization failed")
        print("="*60)
        print("\nNote: First run will download the CLIP model (~350MB)")
        print("This may take several minutes. Try running the test again after.")
        sys.exit(1)

    print("\n" + "="*60)
    print("RESULT: All tests passed!")
    print("="*60)
    print("\nYour MCP server is ready to use!")
    print("Next steps:")
    print("  1. Follow the setup guide in MCP_QUICKSTART.md")
    print("  2. Configure Claude Code with your MCP server")
    print("  3. Restart Claude Code")
    print("  4. Try comparing some images!")


if __name__ == "__main__":
    main()
