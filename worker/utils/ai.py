"""
AI utilities (Claude for analysis/prompts, Imagen for generation)
"""
import anthropic
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import base64
import json
import logging
import re
from typing import Dict, List, Optional
from config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    IMAGEN_MODEL,
    REGION,
    PROJECT_ID,
    VISION_ANALYSIS_MAX_TOKENS,
    PROMPT_GENERATION_MAX_TOKENS,
    ENABLE_PROMPT_REFINEMENT
)

logger = logging.getLogger(__name__)

# Initialize Claude client
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)


def extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Extract JSON from text that may contain markdown code blocks or extra text

    Args:
        text: Raw text that may contain JSON

    Returns:
        Parsed JSON dictionary or None if not found
    """
    # Try to find JSON in markdown code blocks first
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Try parsing the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    return None


async def analyze_image_with_claude(image_path: str) -> Dict[str, any]:
    """
    Analyze image with Claude Haiku (vision model)
    Extracts: primary/accent colors, skin tone, facial expression, pose details,
              clothing details, accessories, hair color/style, body type, distinguishing features

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with enhanced analysis results (14 fields)
    """
    try:
        logger.info(f"Analyzing image with Claude: {image_path}")

        # Read and encode image as base64
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Determine media type
        if image_path.lower().endswith('.png'):
            media_type = "image/png"
        elif image_path.lower().endswith(('.jpg', '.jpeg')):
            media_type = "image/jpeg"
        else:
            media_type = "image/jpeg"  # default

        # Call Claude with vision
        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=VISION_ANALYSIS_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analyze this person's appearance for creating a detailed pixel art avatar.

Return JSON with ALL of these fields:
- primary_colors: array of 2-3 dominant hex colors from clothing (e.g., ["#FF6600", "#000000"])
- accent_colors: array of 1-2 secondary/accent hex colors (e.g., ["#FFFFFF"], or [] if none)
- skin_tone: one of "light", "medium", "tan", "dark", "olive"
- facial_expression: describe expression (e.g., "smiling", "neutral", "serious", "playful")
- pose: main pose (e.g., "standing front-facing", "sitting", "arms crossed")
- pose_detail: specific details (e.g., "relaxed stance, hands in pockets, looking slightly left")
- clothing: brief description (e.g., "orange hoodie and black pants")
- clothing_detail: specific details (e.g., "hoodie has front pocket and drawstrings, pants are fitted")
- accessories: array of accessories (e.g., ["glasses", "hat", "watch"], or [] if none)
- accessory_detail: describe accessories (e.g., "round frame glasses, backwards baseball cap", or "" if no accessories)
- hair_color: color name (e.g., "brown", "blonde", "black", "red")
- hair_style: style description (e.g., "short and spiky", "long wavy", "curly medium length")
- body_type: one of "slim", "average", "athletic", "stocky"
- distinguishing_features: array of unique features (e.g., ["beard", "freckles"], or [] if none)

Only return valid JSON, no explanation."""
                    }
                ]
            }]
        )

        # Parse JSON response
        analysis_text = response.content[0].text
        logger.info(f"Claude response: {analysis_text}")

        # Extract JSON from response (handles markdown code blocks)
        analysis = extract_json_from_text(analysis_text)

        if not analysis:
            logger.error(f"Failed to extract JSON from Claude response: {analysis_text}")
            raise ValueError(f"Could not parse JSON from Claude response: {analysis_text[:200]}")

        # Log analysis details for debugging and quality tracking
        logger.info(f"Vision analysis extracted: "
                   f"{len(analysis.get('distinguishing_features', []))} distinguishing features, "
                   f"{len(analysis.get('accessories', []))} accessories, "
                   f"{len(analysis.get('primary_colors', []))} primary colors, "
                   f"skin tone: {analysis.get('skin_tone', 'unknown')}, "
                   f"expression: {analysis.get('facial_expression', 'unknown')}, "
                   f"body type: {analysis.get('body_type', 'unknown')}")

        logger.info(f"Image analysis complete: {analysis}")
        return analysis

    except ValueError as e:
        logger.error(f"Error parsing Claude response: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing image with Claude: {str(e)}")
        raise


async def generate_imagen_prompt(analysis: Dict[str, any]) -> str:
    """
    Generate optimized Imagen prompt from Claude's image analysis

    Args:
        analysis: Enhanced image analysis dictionary from Claude

    Returns:
        Detailed prompt string for Imagen (100-150 words)
    """
    try:
        logger.info(f"Generating Imagen prompt from analysis: {analysis}")

        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=PROMPT_GENERATION_MAX_TOKENS,
            system="You are an expert at creating detailed, optimized prompts for Google's Imagen AI image generator. You specialize in everskies-style pixel art character avatars with detailed fashion and clothing.",
            messages=[{
                "role": "user",
                "content": f"""Convert this detailed analysis into an optimized Google Imagen prompt for high-quality everskies-style pixel art generation.

Analysis:
{json.dumps(analysis, indent=2)}

Create a prompt for a full-body pixel art character sprite in everskies style following these guidelines:

STRUCTURE YOUR PROMPT IN THIS ORDER:
1. Character Overview: Accurate description matching the person's actual features (skin tone, expression, body type)
2. Physical Accuracy: CRITICAL - Match the person's real features, hair, and distinguishing characteristics exactly
3. Full Body Sprite: "full body character", "standing pose", "complete figure from head to toe"
4. Proportions: "slightly stylized proportions" (not realistic, not chibi - balanced middle ground)
5. DETAILED CLOTHING: VERY IMPORTANT - Describe every clothing item in detail:
   - Specific garment types (hoodie, jeans, jacket, dress, shirt, etc.)
   - Clothing colors with hex values
   - Patterns, textures, designs on clothing (stripes, logos, prints, etc.)
   - Fit and style (oversized, fitted, cropped, etc.)
   - Layering details (jacket over shirt, etc.)
6. Accessories & Details: All accessories mentioned (glasses style, jewelry, hat type, shoes, bags, etc.)
7. Hair Details: Color, length, style, texture
8. Style Keywords: CRITICAL - Include "Everskies pixel avatar style", "retro pixel art", "clean outlines", "soft shading", "simple but expressive details"
9. Pixel Specifications: "64-128 pixel height character", "visibly pixelated", "low-resolution sprite", "chunky visible pixel blocks"
10. Pose: "neutral standing pose", "arms relaxed at sides", "front-facing"
11. Color & Quality: "limited color palette", "classic Everskies proportions", "vibrant but not oversaturated"
12. Technical Requirements: "pure white background", "centered full-body sprite", "no glow", "no shadows"
13. Negative Constraints: CRITICAL - Avoid anime, chibi, photorealism, 3D rendering, smooth/painted look, blur, anti-aliasing, oversized features

REQUIREMENTS:
- CRITICAL: Match person's EXACT features - hairstyle, hair color, facial hair, skin tone, outfit, accessories, overall style
- CRITICAL: DETAILED CLOTHING - every garment, pattern, texture, fit, layering (silhouette and colors must match)
- CRITICAL: "Everskies pixel avatar style" with "retro pixel art", "clean outlines", "soft shading"
- Character specs: "64-128 pixel height", "visibly pixelated", "low-resolution sprite", not smooth/painted
- Pose: "neutral standing pose", "arms relaxed at sides", "front-facing"
- Use specific hex color values for ALL clothing items
- Include ALL distinguishing features and accessories from analysis
- "Limited color palette" and "classic Everskies proportions" (slightly stylized but recognizable)
- Full body sprite (head to toe) including shoes
- "Pure white background", "no glow", "no shadows" - clean sprite only
- NEVER use: anime, chibi, photorealism, 3D, smooth gradients, blur, oversized features
- EMPHASIZE: "simple but expressive details", chunky visible pixels, clearly pixelated aesthetic
- Keep as single flowing paragraph
- Target ~150-200 words for detailed clothing descriptions
- Match the person's clothing silhouette and colors while remaining clearly pixelated

Return ONLY the prompt text, no explanation or formatting."""
            }]
        )

        raw_prompt = response.content[0].text.strip()
        logger.info(f"Generated raw prompt: {raw_prompt}")

        # Apply refinement if enabled
        if ENABLE_PROMPT_REFINEMENT:
            refined_prompt = refine_imagen_prompt(raw_prompt, analysis)
            logger.info(f"Refined prompt: {refined_prompt}")

            # Log prompt quality statistics
            logger.info(f"Prompt quality metrics: "
                       f"length={len(refined_prompt)} chars, "
                       f"words={len(refined_prompt.split())}, "
                       f"refinement=enabled")

            return refined_prompt

        # Log prompt statistics for non-refined path
        logger.info(f"Prompt quality metrics: "
                   f"length={len(raw_prompt)} chars, "
                   f"words={len(raw_prompt.split())}, "
                   f"refinement=disabled")

        return raw_prompt

    except Exception as e:
        logger.error(f"Error generating Imagen prompt: {str(e)}")
        raise


def refine_imagen_prompt(raw_prompt: str, analysis: dict) -> str:
    """
    Post-process the generated prompt to ensure quality keywords and structure.

    Args:
        raw_prompt: The prompt generated by Claude
        analysis: The vision analysis dict

    Returns:
        Refined prompt with quality enhancements
    """
    # Extract critical elements
    colors = analysis.get("primary_colors", [])

    # Ensure color hex values are included
    color_str = ", ".join(colors) if colors else ""
    if color_str and color_str not in raw_prompt:
        raw_prompt = f"{raw_prompt} Primary colors: {color_str}."

    # Ensure quality keywords are present for Everskies-style pixel art
    quality_keywords = {
        "Everskies": "Everskies",
        "retro pixel art": "retro pixel",
        "clean outlines": "clean outlines",
        "64-128 pixel height": "pixel height",
        "visibly pixelated": "visibly pixelated",
        "neutral standing pose": "standing pose",
        "arms relaxed": "arms relaxed",
        "limited color palette": "limited color",
        "white background": "white background",
        "no glow": "no glow"
    }

    for check_keyword in quality_keywords.values():
        if check_keyword.lower() not in raw_prompt.lower():
            # Add missing critical keywords
            if check_keyword == "white background":
                raw_prompt = f"{raw_prompt} Set on a pure white background with no glow or shadows."
            elif check_keyword == "Everskies":
                raw_prompt = f"{raw_prompt} Rendered in Everskies pixel avatar style."
            elif check_keyword == "retro pixel":
                raw_prompt = f"{raw_prompt} Retro pixel art aesthetic with clean outlines."
            elif check_keyword == "clean outlines":
                raw_prompt = f"{raw_prompt} Features clean, distinct pixel outlines."
            elif check_keyword == "pixel height":
                raw_prompt = f"{raw_prompt} Character is 64-128 pixels in height."
            elif check_keyword == "visibly pixelated":
                raw_prompt = f"{raw_prompt} Visibly pixelated low-resolution sprite style."
            elif check_keyword == "standing pose":
                raw_prompt = f"{raw_prompt} Character in neutral standing pose."
            elif check_keyword == "arms relaxed":
                raw_prompt = f"{raw_prompt} Arms relaxed at sides."
            elif check_keyword == "limited color":
                raw_prompt = f"{raw_prompt} Uses a limited color palette in classic Everskies proportions."
            elif check_keyword == "no glow":
                raw_prompt = f"{raw_prompt} No glow effects or shadows."

    # Add negative prompt guidance (from art_gen_prompt.md)
    if "avoid" not in raw_prompt.lower():
        raw_prompt = f"{raw_prompt} Avoid anime, chibi, photorealism, 3D rendering, smooth/painted look, blur, anti-aliasing, and oversized features."

    return raw_prompt


async def generate_pixel_art_with_imagen(prompt: str, output_path: str) -> str:
    """
    Generate pixel art with Google Imagen 3

    Args:
        prompt: Text prompt for image generation
        output_path: Path to save generated image

    Returns:
        Path to generated image
    """
    try:
        logger.info(f"Generating pixel art with Imagen. Prompt: {prompt}")

        # Initialize Imagen model
        model = ImageGenerationModel.from_pretrained(IMAGEN_MODEL)

        # Generate image with minimal parameters
        # Using only guaranteed supported parameters
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1
        )

        # Save first image
        if response.images:
            response.images[0].save(output_path)
            logger.info(f"Pixel art generated and saved to {output_path}")
            return output_path
        else:
            raise ValueError("No images generated by Imagen")

    except Exception as e:
        logger.error(f"Error generating pixel art with Imagen: {str(e)}")
        raise
