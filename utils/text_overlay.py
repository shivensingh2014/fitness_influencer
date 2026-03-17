"""
Text overlay utility for carousel images.
Adds eye-catching text to images in bold, high-contrast format.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

def add_text_overlay(
    image_path: str,
    text: str,
    output_path: str = None,
    position: str = "bottom",
    font_size: int = None,
    text_color: tuple = (255, 255, 255),
    bg_color: tuple = (0, 0, 0, 180),
) -> str:
    """
    Add text overlay to an image in eye-catching format.
    
    Parameters:
      image_path     - Path to source image
      text           - Text to overlay (max 3 words recommended)
      output_path    - Where to save (default: image_path with _overlay suffix)
      position       - "top", "center", or "bottom"
      font_size      - Font size (auto if None)
      text_color     - RGB tuple for text color
      bg_color       - RGBA tuple for background color
    
    Returns:
      Path to the output image with overlay
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Open image
    img = Image.open(img_path)
    width, height = img.size
    
    # Convert to RGB if needed
    if img.mode in ("RGBA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    
    # Create overlay image for text background
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Try to load a bold font, fallback to default
    try:
        # Try common system font paths
        font = ImageFont.truetype("arial.ttf", font_size or 80)
    except:
        try:
            font = ImageFont.truetype("/Windows/Fonts/ariblk.ttf", font_size or 80)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size or 80)
            except:
                font = ImageFont.load_default()
    
    # Wrap text if too long
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(current_line) >= 2:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    
    text_to_draw = "\n".join(lines[:2])  # Max 2 lines
    
    # Get text bounding box
    bbox = draw_overlay.textbbox((0, 0), text_to_draw, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Add padding
    padding = 30
    bg_width = text_width + (padding * 2)
    bg_height = text_height + (padding * 2)
    
    # Determine position
    if position == "top":
        x = (width - bg_width) // 2
        y = 40
    elif position == "center":
        x = (width - bg_width) // 2
        y = (height - bg_height) // 2
    else:  # bottom
        x = (width - bg_width) // 2
        y = height - bg_height - 40
    
    # Draw semi-transparent background rectangle
    draw_overlay.rectangle(
        [(x, y), (x + bg_width, y + bg_height)],
        fill=bg_color
    )
    
    # Draw text
    text_x = x + padding
    text_y = y + padding
    draw_overlay.text(
        (text_x, text_y),
        text_to_draw,
        font=font,
        fill=text_color
    )
    
    # Composite overlay onto image
    img = img.convert("RGB")
    img.paste(overlay, (0, 0), overlay)
    
    # Save
    if output_path is None:
        output_path = str(img_path.parent / f"{img_path.stem}_overlay{img_path.suffix}")
    
    img.save(output_path, "JPEG" if output_path.lower().endswith(".jpg") else "PNG", quality=95)
    
    return output_path


def add_carousel_overlays(image_paths: list[str], texts: list[str]) -> list[str]:
    """
    Add text overlays to carousel images forming a story sequence.
    
    Parameters:
      image_paths - List of image paths
      texts       - List of text overlays (one per image)
    
    Returns:
      List of output image paths with overlays
    """
    if len(image_paths) != len(texts):
        raise ValueError(f"Mismatch: {len(image_paths)} images, {len(texts)} texts")
    
    output_paths = []
    for i, (img_path, text) in enumerate(zip(image_paths, texts), start=1):
        try:
            # Position varies: bottom for most slides, top for first
            position = "top" if i == 1 else "bottom"
            
            output = add_text_overlay(
                img_path,
                text,
                position=position,
                font_size=70,
                text_color=(255, 255, 255),
                bg_color=(0, 0, 0, 200),  # Semi-transparent black
            )
            output_paths.append(output)
        except Exception as e:
            print(f"Warning: Could not add overlay to slide {i}: {e}")
            # Return original if overlay fails
            output_paths.append(img_path)
    
    return output_paths
