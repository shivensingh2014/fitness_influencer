"""
Tests for streamlit_app.py – validates the Streamlit UI module is importable,
its helper functions work correctly, and session-state defaults are well-defined.

All Streamlit runtime dependencies (st.session_state, st.set_page_config, etc.)
are mocked so tests run offline without launching a Streamlit server.
"""
import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Fixtures ──────────────────────────────────────────────────────────

class _AttrDict(dict):
    """Dict subclass that mirrors Streamlit's session_state (attribute access)."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


@pytest.fixture
def mock_streamlit():
    """
    Replace the 'streamlit' module with a MagicMock so importing
    streamlit_app doesn't trigger real Streamlit runtime calls.

    Key: buttons / interactive widgets return False so no action
    branch executes during import.
    """
    mock_st = MagicMock()
    mock_st.session_state = _AttrDict()

    # Widgets return non-truthy defaults to prevent action branches
    mock_st.button.return_value = False
    mock_st.text_area.return_value = ""

    # st.columns returns context managers
    col_mock = MagicMock()
    col_mock.__enter__ = MagicMock(return_value=col_mock)
    col_mock.__exit__ = MagicMock(return_value=False)
    col_mock.button = MagicMock(return_value=False)
    mock_st.columns.return_value = [col_mock, col_mock]

    # st.spinner context manager
    spinner_mock = MagicMock()
    spinner_mock.__enter__ = MagicMock(return_value=spinner_mock)
    spinner_mock.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value = spinner_mock

    original = sys.modules.get("streamlit")
    sys.modules["streamlit"] = mock_st
    yield mock_st
    # Restore
    if original is not None:
        sys.modules["streamlit"] = original
    else:
        sys.modules.pop("streamlit", None)
    # Remove cached streamlit_app module so next import is fresh
    sys.modules.pop("streamlit_app", None)


@pytest.fixture
def app_module(mock_streamlit):
    """Import (or reload) streamlit_app under the mocked Streamlit."""
    sys.modules.pop("streamlit_app", None)
    import streamlit_app
    return streamlit_app


# ── Tests ─────────────────────────────────────────────────────────────

class TestStreamlitAppImport:
    """Verify the app module can be imported without errors."""

    def test_module_is_importable(self, app_module):
        """streamlit_app should import without raising."""
        assert app_module is not None

    def test_module_has_docstring(self, app_module):
        """Module should have a descriptive docstring."""
        assert app_module.__doc__ is not None
        assert "Genfluence" in app_module.__doc__


class TestSessionStateDefaults:
    """Verify session-state defaults are complete and well-typed."""

    def test_defaults_dict_exists(self, app_module):
        """_DEFAULTS should be defined in the module."""
        assert hasattr(app_module, "_DEFAULTS")
        assert isinstance(app_module._DEFAULTS, dict)

    def test_phase_default_is_input(self, app_module):
        assert app_module._DEFAULTS["phase"] == "input"

    def test_max_attempts_default(self, app_module):
        assert app_module._DEFAULTS["max_attempts"] == 5

    def test_required_keys_present(self, app_module):
        """All keys needed by the 4-phase UI should exist."""
        required_keys = {
            "phase", "creative_direction", "image_path", "caption",
            "attempt", "max_attempts", "ig_logged_in", "preflight_done",
            "error", "post_result",
        }
        assert required_keys.issubset(app_module._DEFAULTS.keys())

    def test_boolean_defaults(self, app_module):
        """Boolean flags should default to False."""
        assert app_module._DEFAULTS["ig_logged_in"] is False
        assert app_module._DEFAULTS["preflight_done"] is False

    def test_error_default_is_none(self, app_module):
        assert app_module._DEFAULTS["error"] is None

    def test_post_result_default_is_none(self, app_module):
        assert app_module._DEFAULTS["post_result"] is None


class TestHelperFunctions:
    """Verify helper functions exist and have correct signatures."""

    def test_preflight_checks_exists(self, app_module):
        assert callable(app_module._preflight_checks)

    def test_run_generation_exists(self, app_module):
        assert callable(app_module._run_generation)

    def test_run_posting_exists(self, app_module):
        assert callable(app_module._run_posting)

    def test_run_generation_accepts_two_args(self, app_module):
        """_run_generation should accept (creative_direction, post_type_brief)."""
        import inspect
        sig = inspect.signature(app_module._run_generation)
        params = list(sig.parameters.keys())
        assert len(params) == 2
        assert "creative_direction" in params
        assert "post_type_brief" in params

    def test_run_posting_accepts_two_args(self, app_module):
        """_run_posting should accept (image_path, caption)."""
        import inspect
        sig = inspect.signature(app_module._run_posting)
        params = list(sig.parameters.keys())
        assert len(params) == 2
        assert "image_path" in params
        assert "caption" in params


class TestPreflightChecks:
    """Test the _preflight_checks function with mocked dependencies."""

    def test_fails_without_gemini_key(self, app_module, mock_streamlit):
        """Should fail and set error when GEMINI_API_KEY is empty."""
        mock_streamlit.session_state = _AttrDict(app_module._DEFAULTS)
        with patch("streamlit_app.st", mock_streamlit), \
             patch("config.GEMINI_API_KEY", ""):
            result = app_module._preflight_checks()
        assert result is False

    def test_passes_with_valid_config(self, app_module, mock_streamlit, tmp_path):
        """Should pass when all config values are present and valid."""
        char_img = tmp_path / "character.png"
        char_img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        mock_streamlit.session_state = _AttrDict(app_module._DEFAULTS)
        mock_streamlit.session_state["ig_logged_in"] = True

        with patch("streamlit_app.st", mock_streamlit), \
             patch("config.GEMINI_API_KEY", "test-key"), \
             patch("config.BASE_CHARACTER_IMAGE", str(char_img)), \
             patch("config.INSTAGRAM_USERNAME", ""), \
             patch("requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            result = app_module._preflight_checks()
        assert result is True
