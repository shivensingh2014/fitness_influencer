"""
Tests for utility tools – google_search, nano_banana (generate_image),
instagram_tool (post_to_instagram), post_types, and review module.
All external API calls are mocked.
"""
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import base64

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ═══════════════════════════════════════════════════════════════════════
#  post_types.py
# ═══════════════════════════════════════════════════════════════════════

class TestPostTypes:
    """Tests for utils/post_types.py."""

    def test_post_types_list_not_empty(self):
        from utils.post_types import POST_TYPES
        assert len(POST_TYPES) > 0

    def test_each_post_type_has_name_and_brief(self):
        from utils.post_types import POST_TYPES
        for pt in POST_TYPES:
            assert "name" in pt, f"Post type missing 'name': {pt}"
            assert "brief" in pt, f"Post type missing 'brief': {pt}"
            assert len(pt["name"]) > 3
            assert len(pt["brief"]) > 20

    def test_pick_random_post_type_returns_dict(self):
        from utils.post_types import pick_random_post_type
        result = pick_random_post_type()
        assert isinstance(result, dict)
        assert "name" in result
        assert "brief" in result

    def test_pick_random_is_from_list(self):
        from utils.post_types import pick_random_post_type, POST_TYPES
        result = pick_random_post_type()
        names = [pt["name"] for pt in POST_TYPES]
        assert result["name"] in names

    def test_get_all_post_type_names(self):
        from utils.post_types import get_all_post_type_names, POST_TYPES
        names = get_all_post_type_names()
        assert len(names) == len(POST_TYPES)
        assert all(isinstance(n, str) for n in names)

    def test_at_least_10_post_types(self):
        """The project should have at least 10 diverse post types."""
        from utils.post_types import POST_TYPES
        assert len(POST_TYPES) >= 10


# ═══════════════════════════════════════════════════════════════════════
#  review.py
# ═══════════════════════════════════════════════════════════════════════

class TestReview:
    """Tests for utils/review.py."""

    def test_extract_image_and_caption_from_formatted_output(self, tmp_image, sample_caption):
        from utils.review import extract_image_and_caption
        crew_output = f"Generated image at {tmp_image}\n\n{sample_caption}"
        image_path, caption = extract_image_and_caption(crew_output)
        assert image_path == tmp_image
        assert "tokyo" in caption.lower() or "Rise" in caption

    def test_extract_image_and_caption_fallback_scans_output_dir(self, tmp_image):
        """When no path appears in text, it should scan the output dir."""
        from utils.review import extract_image_and_caption
        crew_output = "CAPTION: Test caption\nHASHTAGS: #test #pytest"
        # tmp_image fixture already created a file in OUTPUT_DIR
        image_path, caption = extract_image_and_caption(crew_output)
        # Caption should be extracted regardless
        assert "Test caption" in caption

    def test_extract_caption_markers(self):
        from utils.review import extract_image_and_caption
        crew_output = (
            "CAPTION: Morning workout in Bali 🌴\n"
            "HASHTAGS: #bali #fitness #travel #morning #wellness"
        )
        _, caption = extract_image_and_caption(crew_output)
        assert "Bali" in caption
        assert "#bali" in caption

    def test_display_review_does_not_crash(self, tmp_image, capsys):
        """Smoke test: display_review should print without crashing."""
        from utils.review import display_review
        # Patch open_image to avoid actually opening a file
        with patch("utils.review.open_image"):
            display_review(tmp_image, "Test caption 🏋️\n\n#test #fitness")
        captured = capsys.readouterr()
        assert "REVIEW" in captured.out or "Caption" in captured.out

    def test_ask_approval_yes(self, monkeypatch):
        from utils.review import ask_approval
        monkeypatch.setattr("builtins.input", lambda _: "yes")
        assert ask_approval() is True

    def test_ask_approval_no(self, monkeypatch):
        from utils.review import ask_approval
        monkeypatch.setattr("builtins.input", lambda _: "no")
        assert ask_approval() is False

    def test_ask_approval_y_shorthand(self, monkeypatch):
        from utils.review import ask_approval
        monkeypatch.setattr("builtins.input", lambda _: "y")
        assert ask_approval() is True


# ═══════════════════════════════════════════════════════════════════════
#  google_search_tool.py
# ═══════════════════════════════════════════════════════════════════════

class TestGoogleSearchTool:
    """Tests for utils/google_search_tool.py (API calls are mocked)."""

    @patch("utils.google_search_tool.genai")
    def test_google_search_returns_string(self, mock_genai):
        """google_search should return a text summary."""
        mock_model = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Top 5 fitness trends: HIIT, yoga, cold plunge, zone 2, calisthenics"
        mock_model.generate_content.return_value = mock_resp
        mock_genai.GenerativeModel.return_value = mock_model

        from utils.google_search_tool import google_search
        result = google_search.run("trending fitness 2026")
        assert isinstance(result, str)
        assert len(result) > 10

    @patch("utils.google_search_tool.genai")
    def test_google_search_caches_results(self, mock_genai):
        """Same query should return cached result without second API call."""
        mock_model = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = "Cached result"
        mock_model.generate_content.return_value = mock_resp
        mock_genai.GenerativeModel.return_value = mock_model

        from utils.google_search_tool import google_search, _search_cache
        _search_cache.clear()

        # First call – hits API
        google_search.run("cache test query xyz123")
        call_count_1 = mock_model.generate_content.call_count

        # Second call – should hit cache
        google_search.run("cache test query xyz123")
        call_count_2 = mock_model.generate_content.call_count

        assert call_count_2 == call_count_1  # no extra API call

    @patch("utils.google_search_tool.genai")
    def test_google_search_handles_api_error(self, mock_genai):
        """Should return an error string, not raise, on API failure."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model

        from utils.google_search_tool import google_search, _search_cache
        _search_cache.clear()

        result = google_search.run("will fail query abc789")
        assert "ERROR" in result or "error" in result.lower()


# ═══════════════════════════════════════════════════════════════════════
#  nano_banana_tool.py (generate_image)
# ═══════════════════════════════════════════════════════════════════════

class TestNanoBananaTool:
    """Tests for utils/nano_banana_tool.py (API calls are mocked)."""

    @patch("utils.nano_banana_tool.requests.post")
    def test_generate_image_success(self, mock_post, tmp_path, monkeypatch):
        """Should save the image and return a file path."""
        # Prepare a fake API response with base64 image data
        fake_image_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        fake_b64 = base64.b64encode(fake_image_bytes).decode()

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "inlineData": {"mimeType": "image/png", "data": fake_b64}
                    }]
                }
            }]
        }
        mock_resp.content = b"OK"
        mock_post.return_value = mock_resp

        from utils.nano_banana_tool import generate_image
        result = generate_image.run("A fitness influencer doing yoga on a rooftop")
        assert result.endswith(".png") or "generated_" in result

    @patch("utils.nano_banana_tool.requests.post")
    def test_generate_image_rate_limit(self, mock_post, tmp_path, monkeypatch):
        """Should return a clear error on HTTP 429."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Quota exhausted"
        mock_resp.content = b"429"
        mock_post.return_value = mock_resp

        from utils.nano_banana_tool import generate_image
        result = generate_image.run("test prompt")
        assert "ERROR" in result
        assert "429" in result or "rate" in result.lower() or "limit" in result.lower()

    @patch("utils.nano_banana_tool.requests.post")
    def test_generate_image_api_error(self, mock_post, tmp_path, monkeypatch):
        """Should return an error string on non-200 responses."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal server error"
        mock_resp.content = b"500"
        mock_post.return_value = mock_resp

        from utils.nano_banana_tool import generate_image
        result = generate_image.run("test prompt")
        assert "ERROR" in result

    @patch("utils.nano_banana_tool.requests.post")
    def test_generate_image_network_error(self, mock_post, tmp_path, monkeypatch):
        """Should return an error string on network failure."""
        import requests as req
        mock_post.side_effect = req.RequestException("Connection refused")

        from utils.nano_banana_tool import generate_image
        result = generate_image.run("test prompt")
        assert "ERROR" in result


# ═══════════════════════════════════════════════════════════════════════
#  instagram_tool.py
# ═══════════════════════════════════════════════════════════════════════

class TestInstagramTool:
    """Tests for utils/instagram_tool.py (all Instagram calls are mocked)."""

    def test_preflight_login_missing_creds(self, monkeypatch):
        """Should raise RuntimeError when creds are empty."""
        monkeypatch.setenv("INSTAGRAM_USERNAME", "")
        monkeypatch.setenv("INSTAGRAM_PASSWORD", "")

        # Need to reload config so the empty env vars take effect
        import importlib
        import config
        importlib.reload(config)
        import utils.instagram_tool as ig_mod
        importlib.reload(ig_mod)

        with pytest.raises(RuntimeError, match="credentials missing"):
            ig_mod.preflight_login()

    @patch("instagrapi.Client")
    def test_post_to_instagram_file_not_found(self, mock_client_cls, tmp_path):
        """Should return error if image file doesn't exist."""
        from utils.instagram_tool import post_to_instagram
        result = post_to_instagram.run(
            image_path=str(tmp_path / "nonexistent.png"),
            caption="test caption",
        )
        assert "ERROR" in result
        assert "not found" in result.lower()

    @patch("utils.instagram_tool._SHARED_CLIENT")
    def test_post_to_instagram_success(self, mock_shared, tmp_image, mock_instagrapi_client):
        """Should return success with a post URL when everything works."""
        import utils.instagram_tool as ig_mod
        ig_mod._SHARED_CLIENT = mock_instagrapi_client

        from utils.instagram_tool import post_to_instagram
        result = post_to_instagram.run(
            image_path=tmp_image,
            caption="Test caption #fitness",
        )
        assert "SUCCESS" in result or "instagram.com" in result
