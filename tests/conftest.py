"""
Shared pytest fixtures for the fitness_influencer_crew test suite.
All tests import from here automatically.
"""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Make the project root importable ──────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _set_env_defaults(monkeypatch, tmp_path):
    """
    Set safe dummy env vars so config.py never touches real credentials
    and output goes to a temp directory.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "test-fake-key-1234")
    monkeypatch.setenv("GEMINI_LLM_MODEL", "gemini/gemini-2.5-flash-lite")
    monkeypatch.setenv("IMAGE_GEN_MODEL", "gemini-2.5-flash-image")
    monkeypatch.setenv("INSTAGRAM_USERNAME", "test_user")
    monkeypatch.setenv("INSTAGRAM_PASSWORD", "test_pass")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("BASE_CHARACTER_IMAGE", str(tmp_path / "character.png"))

    # Create the fake character image so tools don't crash on missing file
    char_img = tmp_path / "character.png"
    char_img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    (tmp_path / "output").mkdir(exist_ok=True)


@pytest.fixture
def tmp_image(tmp_path):
    """Create a tiny valid-ish PNG file and return its path."""
    img = tmp_path / "output" / "generated_20260309_120000.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    # Minimal PNG header + IHDR so Pillow / basic checks pass
    img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
    return str(img)


@pytest.fixture
def sample_caption():
    """Return a realistic caption string for testing."""
    return (
        "CAPTION: Rise and grind in Tokyo 🏙️💪 Nothing beats a sunrise "
        "workout with a skyline view.\n\n"
        "HASHTAGS: #fitness #travel #tokyo #motivation #grind"
    )


@pytest.fixture
def sample_crew_output(tmp_image, sample_caption):
    """Return a string that looks like real crew output with image path + caption."""
    return f"Image saved to: {tmp_image}\n\n{sample_caption}"


@pytest.fixture
def mock_instagrapi_client():
    """Return a mocked instagrapi.Client that fakes login + upload."""
    client = MagicMock()
    client.account_info.return_value = MagicMock(username="test_user")
    media = MagicMock()
    media.code = "ABC123XYZ"
    client.photo_upload.return_value = media
    return client
