"""
Central configuration for the Genfluence fitness-influencer crew.
All environment variables and paths are managed here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from logger import log

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))

# Ensure directories exist
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Nano Banana (Gemini Image Generation) ──────────────────────────────
BASE_CHARACTER_IMAGE = os.getenv(
    "BASE_CHARACTER_IMAGE", str(ASSETS_DIR / "character.png")
)
# gemini-2.5-flash-image (Nano Banana) – stable image generation model
IMAGE_GEN_MODEL = os.getenv(
    "IMAGE_GEN_MODEL", "gemini-2.5-flash-image"
)

# ── Instagram ──────────────────────────────────────────────────────────
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")

# ── LLM (litellm format used by CrewAI) ───────────────────────────────
# gemini-2.5-flash-lite – cost-efficient, supports search grounding & function calling
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini/gemini-2.5-flash-lite")

# ── Log loaded config (mask secrets) ──────────────────────────────────
log.info("Config loaded")
log.debug("  GEMINI_API_KEY    = %s", ("***" + GEMINI_API_KEY[-4:]) if len(GEMINI_API_KEY) > 4 else "(not set)")
log.debug("  GEMINI_LLM_MODEL  = %s", GEMINI_LLM_MODEL)
log.debug("  IMAGE_GEN_MODEL   = %s", IMAGE_GEN_MODEL)
log.debug("  BASE_CHARACTER_IMAGE = %s", BASE_CHARACTER_IMAGE)
log.debug("  INSTAGRAM_USERNAME = %s", INSTAGRAM_USERNAME or "(not set)")
log.debug("  OUTPUT_DIR        = %s", OUTPUT_DIR)
