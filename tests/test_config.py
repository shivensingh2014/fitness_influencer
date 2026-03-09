"""
Tests for config.py – validates that env vars are loaded and paths are created.
"""
import os
import sys
from pathlib import Path

import pytest

# Project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestConfig:
    """Tests for configuration loading."""

    def test_gemini_api_key_loaded(self):
        """GEMINI_API_KEY should be read from env."""
        from config import GEMINI_API_KEY
        assert GEMINI_API_KEY == "test-fake-key-1234"

    def test_gemini_llm_model_default(self):
        """GEMINI_LLM_MODEL should have a sensible default."""
        from config import GEMINI_LLM_MODEL
        assert "gemini" in GEMINI_LLM_MODEL.lower()

    def test_image_gen_model_default(self):
        """IMAGE_GEN_MODEL should point to an image generation model."""
        from config import IMAGE_GEN_MODEL
        assert "image" in IMAGE_GEN_MODEL.lower() or "flash" in IMAGE_GEN_MODEL.lower()

    def test_instagram_creds_loaded(self):
        """Instagram creds should come from env."""
        from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD
        assert INSTAGRAM_USERNAME == "test_user"
        assert INSTAGRAM_PASSWORD == "test_pass"

    def test_output_dir_exists(self, tmp_path):
        """OUTPUT_DIR should be auto-created by config.py."""
        from config import OUTPUT_DIR
        assert Path(OUTPUT_DIR).exists()

    def test_assets_dir_exists(self):
        """ASSETS_DIR should be auto-created by config.py."""
        from config import ASSETS_DIR
        assert ASSETS_DIR.exists()

    def test_base_dir_is_project_root(self):
        """BASE_DIR should point to the fitness_influencer_crew directory."""
        from config import BASE_DIR
        assert BASE_DIR.name == "fitness_influencer_crew"


class TestLogger:
    """Tests for logger.py."""

    def test_logger_exists(self):
        """The 'genfluence' logger should be importable."""
        from logger import log
        assert log is not None
        assert log.name == "genfluence"

    def test_logger_has_handlers(self):
        """Logger should have at least a console and file handler."""
        from logger import log
        assert len(log.handlers) >= 2

    def test_logger_level_is_debug(self):
        """Logger should capture DEBUG and above."""
        import logging
        from logger import log
        assert log.level == logging.DEBUG

    def test_log_info_does_not_crash(self):
        """Smoke test: calling log.info should not raise."""
        from logger import log
        log.info("Test message from pytest – ignore")


class TestLLM:
    """Tests for llm.py."""

    def test_llm_model_string_exported(self):
        """llm.py should export LLM_MODEL."""
        from llm import LLM_MODEL
        assert LLM_MODEL is not None
        assert isinstance(LLM_MODEL, str)
        assert len(LLM_MODEL) > 0
