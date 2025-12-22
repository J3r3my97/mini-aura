"""
Image processing utilities (background removal, compositing, watermark, isolation)
"""
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
from scipy import ndimage
import numpy as np
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


async def isolate_largest_character(input_path: str) -> str:
    """
    Isolate the largest character from an image with multiple figures.
    Uses background removal + connected component analysis to handle
    DALL-E 3's tendency to generate character sheets with duplicates.

    Args:
        input_path: Path to generated image (may have multiple characters)

    Returns:
        Path to output image with only the largest character
    """
    try:
        logger.info(f"Isolating largest character from {input_path}")

        img = Image.open(input_path)
        needs_bg_removal = False

        # Check if already has transparency
        if img.mode != 'RGBA':
            needs_bg_removal = True
        else:
            alpha = img.getchannel('A')
            min_alpha, max_alpha = alpha.getextrema()
            if min_alpha == max_alpha == 255:
                needs_bg_removal = True

        # Remove background if needed
        if needs_bg_removal:
            logger.info("Removing background for isolation analysis...")
            img = remove(img)

        # Ensure RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Convert to numpy array
        arr = np.array(img)

        # Get alpha channel mask (non-transparent pixels)
        alpha = arr[:, :, 3]
        mask = alpha > 128

        # Label connected components
        labeled, num_features = ndimage.label(mask)

        if num_features == 0:
            logger.warning("No characters found in image, returning original")
            return input_path

        if num_features == 1:
            logger.info("Single character detected, no isolation needed")
            # Still crop to bounds for cleaner output
        else:
            logger.info(f"Found {num_features} separate regions, keeping largest")

        # Find the largest component
        component_sizes = ndimage.sum(mask, labeled, range(1, num_features + 1))
        largest_idx = np.argmax(component_sizes) + 1

        # Create mask for only the largest component
        largest_mask = labeled == largest_idx

        # Find bounding box of largest component
        rows = np.any(largest_mask, axis=1)
        cols = np.any(largest_mask, axis=0)
        y_indices = np.where(rows)[0]
        x_indices = np.where(cols)[0]
        y_min, y_max = y_indices[0], y_indices[-1]
        x_min, x_max = x_indices[0], x_indices[-1]

        # Add padding (5% of dimensions)
        pad_x = int((x_max - x_min) * 0.05)
        pad_y = int((y_max - y_min) * 0.05)
        x_min = max(0, x_min - pad_x)
        x_max = min(img.width, x_max + pad_x + 1)
        y_min = max(0, y_min - pad_y)
        y_max = min(img.height, y_max + pad_y + 1)

        # Mask out everything except the largest component
        masked_arr = arr.copy()
        masked_arr[~largest_mask] = [0, 0, 0, 0]

        # Crop to the bounding box
        cropped = Image.fromarray(masked_arr[y_min:y_max, x_min:x_max])

        # Save
        output_path = input_path.replace("_pixel", "_isolated")
        cropped.save(output_path, "PNG")

        logger.info(f"Isolated character saved to {output_path} ({cropped.width}x{cropped.height}px)")
        return output_path

    except Exception as e:
        logger.error(f"Error isolating character: {str(e)}")
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
        output_path = image_path.replace("_isolated", "_watermarked").replace(".png", "_watermarked.png")
        img.save(output_path, "PNG")

        logger.info(f"Watermarked image saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error adding watermark: {str(e)}")
        raise
