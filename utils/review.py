"""
Review Utility – shows the generated image + caption for human approval
before posting to Instagram.
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logger import log


def open_image(image_path: str) -> None:
    """Open the image using the OS default viewer."""
    img = Path(image_path)
    if not img.exists():
        log.warning("[review] Image not found for preview: %s", image_path)
        print(f"  ⚠️  Could not find image to preview: {image_path}")
        return

    log.info("[review] Opening image for preview: %s", image_path)
    try:
        if sys.platform == "win32":
            os.startfile(str(img))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(img)])
        else:
            subprocess.Popen(["xdg-open", str(img)])
    except Exception as exc:
        log.warning("[review] Could not auto-open image: %s", exc)
        print(f"  ⚠️  Could not auto-open image: {exc}")
        print(f"  📂  Open it manually: {img.resolve()}")


def display_review(image_path: str, caption: str) -> None:
    """Print the review panel with caption and image path."""
    border = "═" * 58
    print(f"\n╔{border}╗")
    print(f"║{'👁️  REVIEW BEFORE POSTING':^58}║")
    print(f"╠{border}╣")
    print(f"║{'':58}║")
    print(f"║  📸 Image: {str(image_path)[:45]:<46}║")
    print(f"║{'':58}║")
    print(f"╠{border}╣")
    print(f"║  📝 Caption + Hashtags:{'':35}║")
    print(f"║{'':58}║")

    # Word-wrap the caption within the box
    for line in caption.split("\n"):
        while len(line) > 54:
            print(f"║  {line[:54]}  ║")
            line = line[54:]
        print(f"║  {line:<54}  ║")

    print(f"║{'':58}║")
    print(f"╚{border}╝")
    print()

    # Also open the image in the OS viewer
    open_image(image_path)


def ask_approval() -> bool:
    """
    Ask the user whether to approve the post.
    Returns True for 'post it', False for 'regenerate'.
    """
    while True:
        print("┌──────────────────────────────────────────────────┐")
        print("│  ✅  Type 'yes' or 'y'  → Post to Instagram     │")
        print("│  ❌  Type 'no'  or 'n'  → Regenerate from start │")
        print("└──────────────────────────────────────────────────┘")
        choice = input("\n👉  Your decision: ").strip().lower()

        if choice in ("yes", "y"):
            log.info("[review] User APPROVED the post")
            return True
        elif choice in ("no", "n"):
            log.info("[review] User REJECTED – will regenerate")
            return False
        else:
            print("  ⚠️  Please type 'yes' or 'no'.\n")


def extract_image_and_caption(crew_output) -> tuple:
    """
    Parse the generation crew output to extract the image path and caption.
    Returns (image_path: str, caption: str).
    """
    output_text = str(crew_output)
    log.debug("[review] Raw crew output:\n%s", output_text[:1000])

    image_path = ""
    caption = ""

    # ── Extract image path ────────────────────────────────────────────
    # The image generator task returns an absolute file path
    # Look for common patterns in the output
    for line in output_text.split("\n"):
        line_stripped = line.strip()
        # Match lines that look like file paths to .png/.jpg files
        if any(ext in line_stripped.lower() for ext in (".png", ".jpg", ".jpeg")):
            # Try to find a valid file path
            for token in line_stripped.split():
                token_clean = token.strip("'\"`,;:")
                if any(ext in token_clean.lower() for ext in (".png", ".jpg", ".jpeg")):
                    candidate = Path(token_clean)
                    if candidate.exists():
                        image_path = str(candidate)
                        break
            if image_path:
                break

    # ── Also scan output directory for the most recent image ──────────
    if not image_path:
        from config import OUTPUT_DIR
        output_dir = Path(OUTPUT_DIR)
        if output_dir.exists():
            images = sorted(
                output_dir.glob("generated_*.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if images:
                image_path = str(images[0])
                log.info("[review] Found latest image in output dir: %s", image_path)

    # ── Extract caption + hashtags ────────────────────────────────────
    # Look for CAPTION: and HASHTAGS: markers
    lines = output_text.split("\n")
    caption_lines = []
    hashtag_lines = []
    in_caption = False
    in_hashtags = False

    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("CAPTION:"):
            in_caption = True
            in_hashtags = False
            caption_lines.append(line.strip()[len("CAPTION:"):].strip())
        elif upper.startswith("HASHTAGS:"):
            in_hashtags = True
            in_caption = False
            hashtag_lines.append(line.strip()[len("HASHTAGS:"):].strip())
        elif in_caption and not upper.startswith("HASHTAGS"):
            caption_lines.append(line.strip())
        elif in_hashtags:
            hashtag_lines.append(line.strip())

    caption_text = " ".join(c for c in caption_lines if c).strip()
    hashtag_text = " ".join(h for h in hashtag_lines if h).strip()

    if caption_text or hashtag_text:
        caption = f"{caption_text}\n\n{hashtag_text}".strip()
    else:
        # Fallback: use the last task output (caption task is the last in gen crew)
        caption = output_text.strip()
        log.warning("[review] Could not parse CAPTION/HASHTAGS markers, using raw output")

    log.info("[review] Extracted image_path: %s", image_path or "(not found)")
    log.info("[review] Extracted caption (first 100 chars): %s", caption[:100])

    return image_path, caption
