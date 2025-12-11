"""
Image processing utilities (background removal, compositing, watermark)
"""
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from typing import Tuple
import logging
import os

logger = logging.getLogger(__name__)


async def remove_background(input_path: str) -> str:
    """
    Remove background from image using rembg (U2Net model)

    Args:
        input_path: Path to input image

    Returns:
        Path to output image with transparent background
    """
    try:
        logger.info(f"Removing background from {input_path}")

        # Read input image
        input_img = Image.open(input_path)

        # Remove background (this takes ~2-3 seconds)
        output_img = remove(input_img)

        # Save output
        output_path = input_path.replace("_input", "_nobg").replace(".jpg", ".png")
        output_img.save(output_path, "PNG")

        logger.info(f"Background removed, saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error removing background: {str(e)}")
        raise


async def composite_images(
    background_path: str,
    foreground_path: str,
    position: str = "bottom-right",
    scale: float = 0.3
) -> str:
    """
    Composite mini-me onto original photo

    Args:
        background_path: Path to background image (original photo)
        foreground_path: Path to foreground image (mini-me pixel art)
        position: Position of mini-me (bottom-right, bottom-left, top-right, top-left)
        scale: Scale of mini-me relative to background height

    Returns:
        Path to composited image
    """
    try:
        logger.info(f"Compositing images: bg={background_path}, fg={foreground_path}")

        # Load images
        bg = Image.open(background_path).convert("RGBA")
        fg = Image.open(foreground_path).convert("RGBA")

        # Resize foreground (mini-me) to scale% of background height
        new_height = int(bg.height * scale)
        aspect = fg.width / fg.height
        new_width = int(new_height * aspect)
        fg = fg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        logger.info(f"Resized mini-me to {new_width}x{new_height}")

        # Calculate position (with 5% margin)
        margin_x = int(bg.width * 0.05)
        margin_y = int(bg.height * 0.05)

        if position == "bottom-right":
            x = bg.width - fg.width - margin_x
            y = bg.height - fg.height - margin_y
        elif position == "bottom-left":
            x = margin_x
            y = bg.height - fg.height - margin_y
        elif position == "top-right":
            x = bg.width - fg.width - margin_x
            y = margin_y
        elif position == "top-left":
            x = margin_x
            y = margin_y
        else:
            # Default to bottom-right
            x = bg.width - fg.width - margin_x
            y = bg.height - fg.height - margin_y

        # Paste foreground onto background (using alpha channel for transparency)
        bg.paste(fg, (x, y), fg)

        # Save composited image
        output_path = background_path.replace("_input", "_composite").replace(".jpg", ".png")
        bg.save(output_path, "PNG")

        logger.info(f"Composited image saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error compositing images: {str(e)}")
        raise


async def add_watermark(
    image_path: str,
    text: str = "mini-me",
    position: str = "bottom-left",
    opacity: float = 0.5
) -> str:
    """
    Add watermark text to image

    Args:
        image_path: Path to input image
        text: Watermark text
        position: Position of watermark
        opacity: Opacity of watermark (0.0 to 1.0)

    Returns:
        Path to watermarked image
    """
    try:
        logger.info(f"Adding watermark to {image_path}")

        # Load image
        img = Image.open(image_path).convert("RGBA")

        # Create transparent overlay for watermark
        watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Calculate text size and position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        margin = 20

        if position == "bottom-left":
            x, y = margin, img.height - text_height - margin
        elif position == "bottom-right":
            x, y = img.width - text_width - margin, img.height - text_height - margin
        elif position == "top-left":
            x, y = margin, margin
        elif position == "top-right":
            x, y = img.width - text_width - margin, margin
        else:
            x, y = margin, img.height - text_height - margin

        # Draw watermark with opacity
        alpha = int(255 * opacity)
        draw.text((x, y), text, fill=(255, 255, 255, alpha), font=font)

        # Composite watermark onto image
        img = Image.alpha_composite(img, watermark)

        # Save
        output_path = image_path.replace("_composite", "_watermarked")
        img.save(output_path, "PNG")

        logger.info(f"Watermarked image saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error adding watermark: {str(e)}")
        raise
