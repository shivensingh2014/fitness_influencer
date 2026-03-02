"""
Nano Banana Tool – AI image generation with character consistency.
Uses the Gemini Image Generation REST API with a fixed reference character image.
"""
import os
import sys
import base64
import mimetypes
import traceback
import requests
from datetime import datetime
from pathlib import Path

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import GEMINI_API_KEY, BASE_CHARACTER_IMAGE, OUTPUT_DIR, IMAGE_GEN_MODEL
from logger import log


@tool("generate_image")
def generate_image(prompt: str) -> str:
    """
    Generate an AI image using Nano Banana (Gemini Image Generation).
    Automatically uses the base character image for face / identity consistency.
    Pass the full scene description as 'prompt'.
    Returns the local file path of the saved generated image.
    """
    log.info("[generate_image] Called with prompt: %s", prompt[:120])

    # ── Validate character image ──────────────────────────────────────
    char_path = Path(BASE_CHARACTER_IMAGE)
    if not char_path.is_absolute():
        char_path = Path(__file__).resolve().parent.parent / char_path
    if not char_path.exists():
        log.error("[generate_image] Character image NOT FOUND: %s", char_path)
        return (
            f"ERROR: Base character image not found at '{char_path}'. "
            "Place your character photo there and try again."
        )

    mime_type = mimetypes.guess_type(str(char_path))[0] or "image/png"
    with open(char_path, "rb") as f:
        raw = f.read()
        image_b64 = base64.b64encode(raw).decode()
    log.info("[generate_image] Loaded character image: %s (%.1f KB, %s)",
             char_path.name, len(raw) / 1024, mime_type)

    # ── Build API request ─────────────────────────────────────────────
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{IMAGE_GEN_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    log.info("[generate_image] API model: %s", IMAGE_GEN_MODEL)

    full_prompt = (
        "IMPORTANT: Keep the EXACT same face, skin tone, hair, and body "
        "features from the reference image attached. The person in the "
        "generated photo must be clearly recognisable as the same individual.\n\n"
        f"Scene description: {prompt}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"inlineData": {"mimeType": mime_type, "data": image_b64}},
                    {"text": full_prompt},
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "temperature": 1.0,
        },
    }

    # ── Call API ──────────────────────────────────────────────────────
    log.info("[generate_image] Sending request to Gemini Image API…")
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=180,
        )
    except requests.RequestException as exc:
        log.error("[generate_image] NETWORK ERROR: %s", exc)
        log.debug("[generate_image] Traceback:\n%s", traceback.format_exc())
        return f"ERROR: Network request failed – {exc}"

    log.info("[generate_image] Response: HTTP %s (%d bytes)", resp.status_code, len(resp.content))

    if resp.status_code == 429:
        detail = resp.text[:500]
        log.error("[generate_image] RATE LIMITED (429):\n%s", detail)
        return f"ERROR: Rate limit hit (HTTP 429). Quota exhausted – {detail[:200]}"

    if resp.status_code != 200:
        detail = resp.text[:500]
        log.error("[generate_image] API ERROR HTTP %s:\n%s", resp.status_code, detail)
        return f"ERROR: Gemini API returned {resp.status_code} – {detail}"

    result = resp.json()

    # ── Extract & save image ──────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(OUTPUT_DIR) / f"generated_{timestamp}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                out_path.write_bytes(img_bytes)
                log.info("[generate_image] SUCCESS – saved %s (%.1f KB)",
                         out_path.name, len(img_bytes) / 1024)
                return str(out_path.resolve())

    # No image in response – log what we DID get
    log.error("[generate_image] No image in response. Keys: %s", list(result.keys()))
    log.debug("[generate_image] Full response:\n%s", str(result)[:1000])
    return "ERROR: The API response did not contain a generated image."
