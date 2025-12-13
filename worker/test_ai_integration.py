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

        # Check all expected keys for enhanced schema (14 fields)
        expected_keys = [
            'primary_colors', 'accent_colors', 'skin_tone', 'facial_expression',
            'pose', 'pose_detail', 'clothing', 'clothing_detail',
            'accessories', 'accessory_detail', 'hair_color', 'hair_style',
            'body_type', 'distinguishing_features'
        ]
        missing_keys = [k for k in expected_keys if k not in result]

        if missing_keys:
            print(f"  ✗ Missing keys: {missing_keys}")
            print(f"  Got: {result}")
            return False

        # Validate data types
        if not isinstance(result['primary_colors'], list):
            print(f"  ✗ primary_colors should be a list, got {type(result['primary_colors'])}")
            return False

        if not isinstance(result['accessories'], list):
            print(f"  ✗ accessories should be a list, got {type(result['accessories'])}")
            return False

        if not isinstance(result['distinguishing_features'], list):
            print(f"  ✗ distinguishing_features should be a list, got {type(result['distinguishing_features'])}")
            return False

        # Validate color format (hex codes)
        for color in result['primary_colors']:
            if not color.startswith('#') or len(color) != 7:
                print(f"  ✗ Invalid color format: {color} (expected #RRGGBB)")
                return False

        print(f"  ✓ Enhanced analysis successful (14 fields)")
        print(f"    Primary colors: {result.get('primary_colors')}")
        print(f"    Skin tone: {result.get('skin_tone')}")
        print(f"    Expression: {result.get('facial_expression')}")
        print(f"    Pose: {result.get('pose')}")
        print(f"    Clothing: {result.get('clothing')}")
        print(f"    Accessories: {result.get('accessories')}")
        print(f"    Hair: {result.get('hair_color')} - {result.get('hair_style')}")
        print(f"    Body type: {result.get('body_type')}")
        print(f"    Features: {result.get('distinguishing_features')}")
        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False
    finally:
        os.unlink(test_image_path)


async def test_claude_prompt_generation():
    """Test Claude prompt generation with enhanced schema"""
    from utils.ai import generate_imagen_prompt

    print("\n✍️  Testing Imagen prompt generation...")

    # Enhanced test analysis with all 14 fields
    test_analysis = {
        "primary_colors": ["#FF6600", "#000000"],
        "accent_colors": ["#FFFFFF"],
        "skin_tone": "medium",
        "facial_expression": "smiling",
        "pose": "standing front-facing",
        "pose_detail": "relaxed stance with arms at sides",
        "clothing": "orange hoodie and black pants",
        "clothing_detail": "hoodie has front pocket and drawstrings",
        "accessories": ["glasses", "hat"],
        "accessory_detail": "round frame glasses, backwards baseball cap",
        "hair_color": "brown",
        "hair_style": "short and spiky",
        "body_type": "average",
        "distinguishing_features": ["beard"]
    }

    try:
        prompt = await generate_imagen_prompt(test_analysis)

        if not prompt or len(prompt) < 100:
            print(f"  ✗ Generated prompt too short (expected ~100-150 words): {len(prompt)} chars")
            return False

        # Quality checks for JRPG pixel art style
        quality_keywords = ["2D pixel art", "pixel art", "sprite", "JRPG", "retro RPG", "white background"]
        missing_keywords = [kw for kw in quality_keywords if kw.lower() not in prompt.lower()]

        if missing_keywords:
            print(f"  ⚠️  Warning: Missing quality keywords: {missing_keywords}")
            # Don't fail, but warn

        print(f"  ✓ Prompt generated successfully")
        print(f"    Length: {len(prompt)} chars (~{len(prompt.split())} words)")
        print(f"    Quality keywords present: {[kw for kw in quality_keywords if kw.lower() in prompt.lower()]}")
        print(f"    Preview: {prompt[:150]}...")
        return True

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


async def test_prompt_quality():
    """Test that generated prompts meet quality standards"""
    from utils.ai import generate_imagen_prompt, refine_imagen_prompt

    print("\n⭐ Testing prompt quality and refinement...")

    test_analysis = {
        "primary_colors": ["#FF6600", "#000000"],
        "accent_colors": [],
        "skin_tone": "medium",
        "facial_expression": "smiling",
        "pose": "standing",
        "pose_detail": "relaxed",
        "clothing": "orange hoodie",
        "clothing_detail": "casual",
        "accessories": [],
        "accessory_detail": "",
        "hair_color": "brown",
        "hair_style": "short",
        "body_type": "average",
        "distinguishing_features": []
    }

    try:
        # Generate prompt
        prompt = await generate_imagen_prompt(test_analysis)

        # Test refinement function
        raw_test_prompt = "A simple character in orange."
        refined = refine_imagen_prompt(raw_test_prompt, test_analysis)

        # Quality checks for generated prompt
        checks_passed = 0
        total_checks = 5

        if len(prompt) >= 100:
            checks_passed += 1
            print(f"  ✓ Length check: {len(prompt)} chars")
        else:
            print(f"  ✗ Length check failed: {len(prompt)} chars (expected >= 100)")

        if "pixel art" in prompt.lower() or "sprite" in prompt.lower() or "jrpg" in prompt.lower():
            checks_passed += 1
            print(f"  ✓ Style keyword present (pixel art/sprite/JRPG)")
        else:
            print(f"  ✗ Missing style keywords")

        if "#FF6600" in prompt or "orange" in prompt.lower():
            checks_passed += 1
            print(f"  ✓ Color details present")
        else:
            print(f"  ✗ Missing color details")

        if "white background" in prompt.lower():
            checks_passed += 1
            print(f"  ✓ Background specification present")
        else:
            print(f"  ✗ Missing background specification")

        if len(refined) > len(raw_test_prompt):
            checks_passed += 1
            print(f"  ✓ Refinement adds content: {len(raw_test_prompt)} → {len(refined)} chars")
        else:
            print(f"  ✗ Refinement didn't enhance prompt")

        print(f"\n  Quality Score: {checks_passed}/{total_checks}")
        return checks_passed >= 3  # Pass if at least 3/5 checks pass

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
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
        ("Prompt Quality & Refinement", test_prompt_quality()),
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
