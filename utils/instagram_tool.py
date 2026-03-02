"""
Instagram Posting Tool – uploads a photo with caption to Instagram.
Uses the `instagrapi` library (Instagram Private API).
"""
import sys
import traceback
from pathlib import Path

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
from logger import log


@tool("post_to_instagram")
def post_to_instagram(image_path: str, caption: str) -> str:
    """
    Post a photo to Instagram.
    Parameters:
      image_path – absolute or relative path to the image file.
      caption    – full caption text including hashtags at the end.
    Returns a success message with the post URL, or an error string.
    """
    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired,
        ChallengeRequired,
        TwoFactorRequired,
    )

    log.info("[instagram] Called with image_path=%s", image_path)
    log.debug("[instagram] Caption: %s", caption[:200])

    img = Path(image_path)
    if not img.exists():
        log.error("[instagram] Image file NOT FOUND: %s", image_path)
        return f"ERROR: Image file not found – {image_path}"

    log.info("[instagram] Image OK: %s (%.1f KB)", img.name, img.stat().st_size / 1024)

    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        log.error("[instagram] Credentials MISSING in .env")
        return (
            "ERROR: Instagram credentials missing. "
            "Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file."
        )

    cl = Client()
    session_file = Path(__file__).resolve().parent.parent / ".ig_session.json"

    # ── Login ─────────────────────────────────────────────────────────
    log.info("[instagram] Logging in as @%s…", INSTAGRAM_USERNAME)
    try:
        if session_file.exists():
            log.debug("[instagram] Loading saved session from %s", session_file)
            cl.load_settings(session_file)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        else:
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(session_file)
        log.info("[instagram] Login successful")
    except (LoginRequired, ChallengeRequired, TwoFactorRequired) as exc:
        log.error("[instagram] Login CHALLENGE: %s", exc)
        log.debug("[instagram] Traceback:\n%s", traceback.format_exc())
        return (
            f"ERROR: Instagram login challenge – {exc}. "
            "Log in manually once or handle 2FA, then retry."
        )
    except Exception as exc:
        log.error("[instagram] Login FAILED: %s", exc)
        log.debug("[instagram] Traceback:\n%s", traceback.format_exc())
        return f"ERROR: Instagram login failed – {exc}"

    # ── Upload ────────────────────────────────────────────────────────
    log.info("[instagram] Uploading photo…")
    try:
        media = cl.photo_upload(path=str(img), caption=caption)
        post_url = f"https://www.instagram.com/p/{media.code}/"
        log.info("[instagram] SUCCESS – posted: %s", post_url)
        return f"SUCCESS: Posted to Instagram ✅\nURL: {post_url}"
    except Exception as exc:
        log.error("[instagram] Upload FAILED: %s", exc)
        log.debug("[instagram] Traceback:\n%s", traceback.format_exc())
        return f"ERROR: Failed to upload photo – {exc}"
