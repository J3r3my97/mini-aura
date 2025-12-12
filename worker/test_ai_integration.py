"""
Local integration test for AI functions
Tests Claude API calls and validates Imagen integration

Usage:
    export CLAUDE_API_KEY="your-key-here"
    export PROJECT_ID="mini-aura"
    python3 test_ai_integration.py

This helps catch API parameter issues before deployment!
"""
import asyncio
import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set required env vars for imports
os.environ.setdefault('PROJECT_ID', 'mini-aura')
os.environ.setdefault('REGION', 'us-central1')

# Check for Claude API key
if not os.getenv('CLAUDE_API_KEY'):
    print("❌ ERROR: CLAUDE_API_KEY environment variable not set")
    print("\nSet it with:")
    print("  export CLAUDE_API_KEY='your-key-here'")
    sys.exit(1)


async def test_claude_json_extraction():
    """Test that we can handle Claude's JSON responses"""
    from utils.ai import extract_json_from_text

    print("\n📝 Testing JSON extraction...")

    # Test various response formats
    test_cases = [
        ('Plain JSON', '{"colors": ["#FF0000"]}'),
        ('Markdown', '```json\n{"colors": ["#FF0000"]}\n```'),
        ('With text', 'Here is the result: {"colors": ["#FF0000"]}')
    ]

    for name, text in test_cases:
        result = extract_json_from_text(text)
        if result and 'colors' in result:
            print(f"  ✓ {name}: PASS")
        else:
            print(f"  ✗ {name}: FAIL - got {result}")
            return False

    return True


async def test_claude_image_analysis():
    """Test Claude image analysis with a test image"""
    from utils.ai import analyze_image_with_claude

    print("\n🖼️  Testing Claude image analysis...")

    # Create a simple test image
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        test_image_path = f.name
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path)

    try:
        result = await analyze_image_with_claude(test_image_path)

        # Check expected keys
        expected_keys = ['primary_colors', 'pose', 'clothing', 'accessories', 'hair_color']
        missing_keys = [k for k in expected_keys if k not in result]

        if missing_keys:
            print(f"  ✗ Missing keys: {missing_keys}")
            print(f"  Got: {result}")
            return False

        print(f"  ✓ Analysis successful")
        print(f"    Primary colors: {result.get('primary_colors')}")
        print(f"    Pose: {result.get('pose')}")
        print(f"    Clothing: {result.get('clothing')}")
        print(f"    Accessories: {result.get('accessories')}")
        print(f"    Hair color: {result.get('hair_color')}")
        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False
    finally:
        os.unlink(test_image_path)


async def test_claude_prompt_generation():
    """Test Claude prompt generation"""
    from utils.ai import generate_imagen_prompt

    print("\n✍️  Testing Imagen prompt generation...")

    test_analysis = {
        "primary_colors": ["#FF6600", "#000000"],
        "pose": "standing front-facing",
        "clothing": "orange hoodie",
        "accessories": ["glasses"],
        "hair_color": "brown"
    }

    try:
        prompt = await generate_imagen_prompt(test_analysis)

        if not prompt or len(prompt) < 10:
            print(f"  ✗ Generated prompt too short: {prompt}")
            return False

        print(f"  ✓ Prompt generated successfully")
        print(f"    Length: {len(prompt)} chars")
        print(f"    Preview: {prompt[:100]}...")
        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


async def test_imagen_api_call():
    """Test Imagen API call with mocked Vertex AI"""
    print("\n🎨 Testing Imagen API call parameters...")

    # Mock the Vertex AI imports and models
    with patch('utils.ai.ImageGenerationModel') as MockImagenModel:
        # Create mock response
        mock_image = Mock()
        mock_response = Mock()
        mock_response.images = [mock_image]

        # Create mock model
        mock_model = Mock()
        mock_model.generate_images.return_value = mock_response
        MockImagenModel.from_pretrained.return_value = mock_model

        # Import and test
        from utils.ai import generate_pixel_art_with_imagen

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            test_output = f.name

        try:
            # Run the function
            await generate_pixel_art_with_imagen(
                "test prompt",
                test_output
            )

            # Verify it was called with correct parameters
            mock_model.generate_images.assert_called_once()
            call_kwargs = mock_model.generate_images.call_args[1]

            # Check parameters
            if 'prompt' not in call_kwargs:
                print("  ✗ Missing required 'prompt' parameter")
                return False

            # Check for unsupported parameters
            unsupported = ['aspect_ratio', 'safety_filter_level', 'person_generation', 'add_watermark']
            found_unsupported = [k for k in unsupported if k in call_kwargs]

            if found_unsupported:
                print(f"  ✗ Using unsupported parameters: {found_unsupported}")
                print(f"  Call kwargs: {call_kwargs}")
                return False

            print(f"  ✓ Imagen API call parameters valid")
            print(f"    Parameters: {list(call_kwargs.keys())}")
            return True

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if os.path.exists(test_output):
                os.unlink(test_output)


async def main():
    """Run all tests"""
    print("="*60)
    print("🧪 AI Integration Tests")
    print("="*60)

    tests = [
        ("JSON Extraction", test_claude_json_extraction()),
        ("Claude Image Analysis", test_claude_image_analysis()),
        ("Claude Prompt Generation", test_claude_prompt_generation()),
        ("Imagen API Parameters", test_imagen_api_call()),
    ]

    results = []
    for name, test_coro in tests:
        try:
            result = await test_coro
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "="*60)
    print("📊 Results Summary")
    print("="*60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)

    print(f"\n{total_passed}/{total_tests} tests passed")
    print("="*60)

    return all(p for _, p in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
