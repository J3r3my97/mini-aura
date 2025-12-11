"""
AI utilities (Claude for analysis/prompts, Imagen for generation)
"""
import anthropic
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import base64
import json
import logging
from typing import Dict, List
from config import CLAUDE_API_KEY, CLAUDE_MODEL, IMAGEN_MODEL, REGION, PROJECT_ID

logger = logging.getLogger(__name__)

# Initialize Claude client
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)


async def analyze_image_with_claude(image_path: str) -> Dict[str, any]:
    """
    Analyze image with Claude Haiku (vision model)
    Extracts: colors, pose, clothing, accessories, hair color

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with analysis results
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
            max_tokens=500,
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
                        "text": """Analyze this person's appearance for creating a pixel art avatar.

Return JSON with:
- primary_colors: array of 2-3 hex colors from clothing (e.g., ["#FF6600", "#000000"])
- pose: describe their pose (e.g., "standing front-facing", "sitting", "arms crossed")
- clothing: brief description (e.g., "orange hoodie and black pants")
- accessories: array of accessories they're wearing (e.g., ["glasses", "hat", "necklace"], or [] if none)
- hair_color: color name (e.g., "brown", "blonde", "black")

Only return valid JSON, no explanation."""
                    }
                ]
            }]
        )

        # Parse JSON response
        analysis_text = response.content[0].text
        logger.info(f"Claude response: {analysis_text}")

        analysis = json.loads(analysis_text)

        logger.info(f"Image analysis complete: {analysis}")
        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing Claude JSON response: {str(e)}")
        logger.error(f"Response was: {analysis_text}")
        raise
    except Exception as e:
        logger.error(f"Error analyzing image with Claude: {str(e)}")
        raise


async def generate_imagen_prompt(analysis: Dict[str, any]) -> str:
    """
    Generate Imagen prompt from Claude's image analysis

    Args:
        analysis: Image analysis dictionary from Claude

    Returns:
        Prompt string for Imagen
    """
    try:
        logger.info(f"Generating Imagen prompt from analysis: {analysis}")

        response = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Convert this analysis into a Google Imagen prompt for pixel art:

{json.dumps(analysis, indent=2)}

Create a prompt for: isometric voxel/LEGO style pixel art character.

Requirements:
- Describe visual details clearly (colors, clothing, accessories, pose)
- Use keywords like: "isometric", "voxel art", "LEGO minifigure", "pixel art"
- Include "simple clean design", "white background"
- Keep it concise (1-2 sentences, ~50 words)
- Format as single paragraph, no line breaks

Only return the prompt text, no explanation."""
            }]
        )

        prompt = response.content[0].text.strip()
        logger.info(f"Generated prompt: {prompt}")

        return prompt

    except Exception as e:
        logger.error(f"Error generating Imagen prompt: {str(e)}")
        raise


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

        # Generate image
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult",
            # Use standard quality (faster, cheaper)
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
