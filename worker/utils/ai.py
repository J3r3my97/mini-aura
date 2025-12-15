"""
AI utilities (Claude for analysis/prompts, DALL-E 3 for generation)
"""
import anthropic
from openai import OpenAI
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import base64
import json
import logging
import re
from typing import Dict, Optional
from config import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    OPENAI_API_KEY,
    DALLE_MODEL,
    DALLE_SIZE,
    DALLE_QUALITY,
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

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

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


async def generate_dalle_prompt(analysis: Dict[str, any]) -> str:
    """
    Generate optimized DALL-E 3 prompt from Claude's image analysis

    Args:
        analysis: Enhanced image analysis dictionary from Claude

    Returns:
        Detailed prompt string for DALL-E 3 with Everskies style focus
    """
    try:
        logger.info(f"Generating DALL-E 3 prompt from analysis: {analysis}")

        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=PROMPT_GENERATION_MAX_TOKENS,
            system="You are an expert prompt engineer for OpenAI DALL-E 3. You specialize in producing clean, consistent, centered, full-body 2D pixel-art fashion doll avatars in the Everskies style. You strictly avoid realism, 3D rendering, anime styles, painterly effects, and background scenes. You prioritize composition, proportion accuracy, and fashion detail.",
            messages=[{
                "role": "user",
                "content": f"""Using this analysis, create a DALL-E 3 prompt following the exact template below.

Analysis:
{json.dumps(analysis, indent=2)}

Template (fill in the bracketed sections):

Create a single 2D pixel-art fashion doll avatar in the Everskies style, one person only, no duplicates, centered in frame.

Front-facing stylized character with Everskies-style proportions: slightly oversized head, slim torso, long legs. True pixel-art style with visible pixel grid, crisp edges, clean outlines, soft flat shading, high readability at small sizes.

[SPECIFIC SKIN TONE], [DETAILED HAIR DESCRIPTION], [FACIAL HAIR IF PRESENT], [SIMPLE FACIAL EXPRESSION ONLY — neutral calm expression or smiling], slightly chibi but proportional body.

Outfit: [VERY DETAILED CLOTHING — fit, fabric texture, layers, patterns, exact colors, top-to-bottom].
Accessories: [ONLY WORN ITEMS — necklaces, bags with strap placement, glasses, shoes].

Neutral standing pose, arms relaxed at sides, feet slightly apart, full body visible from head to shoes. Symmetrical composition.

Minimal lighting, flat colors, muted palette, no shadows, no background or transparent background.

Fashion-focused, clean, modern. NOT realistic, NOT 3D, NOT anime, NOT painterly. No props, no handheld objects, no text, no logos.

🚫 Avoid: photorealism, realism, 3D render, anime, cartoon, painterly style, sketch, watercolor, gradients, dramatic lighting, backgrounds, scenes, props, phones, cameras, text, logos, multiple people, duplicates, cropped body

CRITICAL:
- Use EXACT skin tone from analysis
- NO actions (no "looking at phone", "holding objects")
- NO props or handheld items
- Full body visible, centered, symmetrical

Return ONLY the filled prompt, no explanation."""
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
        logger.error(f"Error generating DALL-E 3 prompt: {str(e)}")
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
    # CRITICAL: Ensure "single character only" is at the start to prevent duplicates
    if "single" not in raw_prompt.lower() and "one person" not in raw_prompt.lower():
        raw_prompt = f"Create a single 2D pixel-art fashion doll avatar, one person only. {raw_prompt}"

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

    # Add negative prompt guidance with emphasis on no duplicates
    if "avoid" not in raw_prompt.lower():
        raw_prompt = f"{raw_prompt} Avoid anime, chibi, photorealism, 3D rendering, smooth/painted look, blur, anti-aliasing, oversized features, multiple people, and duplicates."

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


async def generate_pixel_art_with_dalle(prompt: str, output_path: str) -> str:
    """
    Generate pixel art with OpenAI DALL-E 3

    Args:
        prompt: Text prompt for image generation
        output_path: Path to save generated image

    Returns:
        Path to generated image
    """
    try:
        logger.info(f"Generating pixel art with DALL-E 3. Prompt: {prompt}")

        # Generate image with DALL-E 3 using b64_json to avoid URL download issues
        response = openai_client.images.generate(
            model=DALLE_MODEL,
            prompt=prompt,
            size=DALLE_SIZE,
            quality=DALLE_QUALITY,
            response_format="b64_json",
            n=1
        )

        # Get the base64 image data
        b64_image = response.data[0].b64_json
        logger.info(f"DALL-E 3 generated image (base64)")

        # Decode and save to output path
        image_data = base64.b64decode(b64_image)
        with open(output_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"Pixel art generated and saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error generating pixel art with DALL-E 3: {str(e)}")
        raise
