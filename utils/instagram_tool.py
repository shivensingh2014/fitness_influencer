"""
Instagram Posting Tool – uploads a photo with caption to Instagram.
Uses the `instagrapi` library (Instagram Private API).

Two entry points:
  • preflight_login()    – call early in the pipeline to verify credentials.
                           Returns a logged-in Client and caches it module-wide.
  • post_to_instagram()  – CrewAI tool; reuses the cached Client if available.
"""
import sys
import time
import traceback
from pathlib import Path
from PIL import Image

try:
    from crewai.tools import tool
except ImportError:
    from crewai import tool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
from logger import log

SESSION_FILE = Path(__file__).resolve().parent.parent / ".ig_session.json"

# Module-level cache – set by preflight_login(), reused by post_to_instagram()
_SHARED_CLIENT = None


# ── Low-level helpers ─────────────────────────────────────────────────

def _fresh_login(cl, username, password):
    """Perform a clean login (no saved session) and persist it."""
    log.info("[instagram] Performing FRESH login as @%s…", username)
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        log.debug("[instagram] Deleted stale session file")

    cl.login(username, password)
    cl.dump_settings(SESSION_FILE)
    log.info("[instagram] Fresh login successful – session saved")


def _login(cl, username, password):
    """
    Try to log in using a saved session first; if that fails (stale /
    login_required), fall back to a fresh login.
    """
    from instagrapi.exceptions import LoginRequired

    if SESSION_FILE.exists():
        log.debug("[instagram] Loading saved session from %s", SESSION_FILE)
        cl.load_settings(SESSION_FILE)
        cl.login(username, password)
        try:
            cl.account_info()
            cl.dump_settings(SESSION_FILE)
            log.info("[instagram] Resumed saved session OK")
            return
        except LoginRequired:
            log.warning("[instagram] Saved session is stale – re-authenticating")
        except Exception as exc:
            log.warning("[instagram] Session check failed (%s) – re-authenticating", exc)

    _fresh_login(cl, username, password)


# ── Pre-flight login (called from main.py BEFORE any crew work) ──────

def preflight_login():
    """
    Verify Instagram credentials at pipeline start-up.

    Returns the logged-in `instagrapi.Client` on success.
    Raises an exception (with a user-friendly message) on failure,
    so the pipeline can abort immediately.
    """
    global _SHARED_CLIENT

    from instagrapi import Client

    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        raise RuntimeError(
            "Instagram credentials missing. "
            "Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file."
        )

    cl = Client()
    cl.delay_range = [2, 5]

    _login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    # Extra verification – lightweight API call
    cl.account_info()
    log.info("[instagram] Pre-flight login verified for @%s", INSTAGRAM_USERNAME)

    _SHARED_CLIENT = cl
    return cl


# ── Image conversion helper ──────────────────────────────────────────

def _ensure_jpg_format(image_path: str) -> str:
    """
    Ensure image is in JPG format (Instagram prefers JPG over PNG).
    If the image is PNG or other format, convert to JPG.
    Returns the path to the JPG file (may be same as input if already JPG).
    """
    p = Path(image_path)
    if p.suffix.lower() == ".jpg" or p.suffix.lower() == ".jpeg":
        # Already JPG
        return image_path
    
    # Convert to JPG
    try:
        img = Image.open(image_path)
        # Convert RGBA to RGB (JPG doesn't support transparency)
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode != "RGB":
            img = img.convert("RGB")
        
        jpg_path = p.with_suffix(".jpg")
        img.save(jpg_path, "JPEG", quality=95)
        log.info("[instagram] Converted %s → %s (JPG)", p.name, jpg_path.name)
        return str(jpg_path)
    except Exception as exc:
        log.error("[instagram] Image conversion failed for %s: %s", image_path, exc)
        # Return original path and let the upload fail with a clearer error
        return image_path


# ── Carousel upload (private helper) ──────────────────────────────────

def carousel_upload(image_paths: list[str], caption: str) -> str:
    """
    Post multiple photos as a carousel (album) to Instagram.
    Uses the cached _SHARED_CLIENT or creates a new one.
    Parameters:
      image_paths – list of absolute or relative paths to image files.
      caption     – full caption text including hashtags at the end.
    Returns a success message with the post URL, or an error string.
    """
    global _SHARED_CLIENT

    from instagrapi import Client
    from instagrapi.exceptions import (
        LoginRequired,
        ChallengeRequired,
        TwoFactorRequired,
    )

    if not image_paths:
        return "ERROR: No image paths provided for carousel upload."

    # Validate all files exist and convert to JPG format
    paths = []
    for path_str in image_paths:
        p = Path(path_str)
        if not p.exists():
            log.error("[instagram] Image file NOT FOUND: %s", path_str)
            return f"ERROR: Image file not found – {path_str}"
        # Convert to JPG if needed
        jpg_path = _ensure_jpg_format(str(p))
        paths.append(jpg_path)

    log.info("[instagram] Carousel upload: %d images", len(paths))
    for p in paths:
        log.info("[instagram]   - %s (%.1f KB)", Path(p).name, Path(p).stat().st_size / 1024)

    # Reuse the pre-authenticated client if available
    if _SHARED_CLIENT is not None:
        cl = _SHARED_CLIENT
        log.info("[instagram] Reusing pre-authenticated client for carousel")
    else:
        if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
            log.error("[instagram] Credentials MISSING in .env")
            return (
                "ERROR: Instagram credentials missing. "
                "Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file."
            )
        cl = Client()
        cl.delay_range = [2, 5]
        try:
            _login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        except (ChallengeRequired, TwoFactorRequired) as exc:
            log.error("[instagram] Login CHALLENGE: %s", exc)
            return f"ERROR: Instagram login challenge – {exc}. Log in manually on a browser/phone first, then retry."
        except Exception as exc:
            log.error("[instagram] Login FAILED: %s", exc)
            return f"ERROR: Instagram login failed – {exc}"

    # Validate carousel constraints
    if len(paths) < 2:
        return "ERROR: Carousel requires at least 2 images. You provided " + str(len(paths))
    if len(paths) > 10:
        log.warning("[instagram] Instagram allows max 10 images per carousel, using first 10")
        paths = paths[:10]
    
    # Upload carousel (with one retry on login_required)
    for attempt in range(1, 3):
        log.info("[instagram] Carousel upload attempt %d…", attempt)
        try:
            media = cl.album_upload(paths=[str(p) for p in paths], caption=caption)
            post_url = f"https://www.instagram.com/p/{media.code}/"
            log.info("[instagram] SUCCESS – carousel posted: %s", post_url)
            return f"SUCCESS: Carousel posted to Instagram ✅\nURL: {post_url}"
        except LoginRequired:
            log.warning("[instagram] Got login_required during carousel upload – re-authenticating")
            if attempt == 1:
                try:
                    _fresh_login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                    _SHARED_CLIENT = cl
                    time.sleep(3)
                except Exception as login_exc:
                    log.error("[instagram] Re-login also failed: %s", login_exc)
                    return f"ERROR: Instagram re-login failed – {login_exc}"
            else:
                return (
                    "ERROR: Instagram keeps returning 'login_required'. "
                    "Your account may need a manual login (challenge/2FA) first. "
                    "Open Instagram in a browser, log in, then retry."
                )
        except Exception as exc:
            log.error("[instagram] Carousel upload FAILED: %s", exc)
            log.debug("[instagram] Full traceback:\n%s", traceback.format_exc())
            
            # Provide more helpful error messages
            err_str = str(exc).lower()
            if "image" in err_str or "format" in err_str or "jpg" in err_str or "png" in err_str:
                return (
                    f"ERROR: Image format/validation failed – {exc}\n"
                    "Try ensuring all images are JPG/PNG, properly sized, and not corrupted."
                )
            elif "unknown" in err_str and "{}" in str(exc):
                return (
                    f"ERROR: Instagram API returned unknown error. "
                    "This may indicate the images are incompatible. "
                    "Ensure images are JPG/PNG, landscape orientation recommended."
                )
            else:
                return f"ERROR: Failed to upload carousel – {exc}"

    return "ERROR: Carousel upload failed after all retries."


# ── CrewAI tool ───────────────────────────────────────────────────────

@tool("post_to_instagram")
def post_to_instagram(image_path: str, caption: str) -> str:
    """
    Post a photo to Instagram.
    Parameters:
      image_path – absolute or relative path to the image file (or comma-separated list for carousel).
      caption    – full caption text including hashtags at the end.
    Returns a success message with the post URL, or an error string.
    """
    global _SHARED_CLIENT

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

    # Convert to JPG if needed
    jpg_image_path = _ensure_jpg_format(image_path)
    img = Path(jpg_image_path)

    log.info("[instagram] Image OK: %s (%.1f KB)", img.name, img.stat().st_size / 1024)

    # Reuse the pre-authenticated client if available, else create a new one
    if _SHARED_CLIENT is not None:
        cl = _SHARED_CLIENT
        log.info("[instagram] Reusing pre-authenticated client")
    else:
        if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
            log.error("[instagram] Credentials MISSING in .env")
            return (
                "ERROR: Instagram credentials missing. "
                "Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in your .env file."
            )
        cl = Client()
        cl.delay_range = [2, 5]
        try:
            _login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        except (ChallengeRequired, TwoFactorRequired) as exc:
            log.error("[instagram] Login CHALLENGE: %s", exc)
            return (
                f"ERROR: Instagram login challenge – {exc}. "
                "Log in manually on a browser/phone first, then retry."
            )
        except Exception as exc:
            log.error("[instagram] Login FAILED: %s", exc)
            return f"ERROR: Instagram login failed – {exc}"

    # ── Upload (with one retry on login_required) ─────────────────────
    for attempt in range(1, 3):
        log.info("[instagram] Upload attempt %d…", attempt)
        try:
            media = cl.photo_upload(path=str(img), caption=caption)
            post_url = f"https://www.instagram.com/p/{media.code}/"
            log.info("[instagram] SUCCESS – posted: %s", post_url)
            return f"SUCCESS: Posted to Instagram ✅\nURL: {post_url}"
        except LoginRequired:
            log.warning("[instagram] Got login_required during upload – re-authenticating")
            if attempt == 1:
                try:
                    _fresh_login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                    _SHARED_CLIENT = cl  # update cache
                    time.sleep(3)
                except Exception as login_exc:
                    log.error("[instagram] Re-login also failed: %s", login_exc)
                    return f"ERROR: Instagram re-login failed – {login_exc}"
            else:
                return (
                    "ERROR: Instagram keeps returning 'login_required'. "
                    "Your account may need a manual login (challenge/2FA) first. "
                    "Open Instagram in a browser, log in, then retry."
                )
        except Exception as exc:
            log.error("[instagram] Upload FAILED: %s", exc)
            log.debug("[instagram] Traceback:\n%s", traceback.format_exc())
            return f"ERROR: Failed to upload photo – {exc}"

    return "ERROR: Upload failed after all retries."
