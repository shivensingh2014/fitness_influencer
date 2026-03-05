"""
🚀 Genfluence – Streamlit UI

Launch:
    cd fitness_influencer_crew
    streamlit run streamlit_app.py
"""
import sys
import time
from pathlib import Path

# Ensure the package root is on sys.path so all imports resolve
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from logger import log

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Genfluence – AI Influencer Pipeline",
    page_icon="🚀",
    layout="centered",
)

# ── Session‑state defaults ────────────────────────────────────────────
_DEFAULTS = {
    "phase": "input",           # input → review → posting → done
    "creative_direction": "",
    "image_path": "",
    "caption": "",
    "attempt": 0,
    "max_attempts": 5,
    "ig_logged_in": False,
    "preflight_done": False,
    "error": None,
    "post_result": None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────

def _preflight_checks() -> bool:
    """Run pre‑flight checks (Instagram login + Gemini quota).
    Returns True on success, sets st.session_state.error on failure."""
    from config import GEMINI_API_KEY, BASE_CHARACTER_IMAGE, INSTAGRAM_USERNAME

    # Gemini key
    if not GEMINI_API_KEY:
        st.session_state.error = (
            "❌ **GEMINI_API_KEY** is not set. Fill it in your `.env` file."
        )
        return False

    # Character image
    char_img = Path(BASE_CHARACTER_IMAGE)
    if not char_img.is_absolute():
        char_img = Path(__file__).parent / char_img
    if not char_img.exists():
        st.session_state.error = (
            f"❌ Base character image not found at `{char_img}`. "
            "Place your character photo there and reload."
        )
        return False

    # Instagram login
    ig_enabled = bool(INSTAGRAM_USERNAME)
    if ig_enabled and not st.session_state.ig_logged_in:
        from utils.instagram_tool import preflight_login
        try:
            preflight_login()
            st.session_state.ig_logged_in = True
            log.info("[streamlit] Instagram login OK")
        except Exception as exc:
            st.session_state.error = (
                f"❌ **Instagram login failed:** {exc}\n\n"
                "Check `INSTAGRAM_USERNAME` / `INSTAGRAM_PASSWORD` in `.env`, "
                "or clear any challenge by logging in via a browser first."
            )
            return False

    # Gemini quota check
    import requests as _req
    _test_url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    )
    _test_body = {"contents": [{"parts": [{"text": "Say OK"}]}]}
    try:
        r = _req.post(_test_url, json=_test_body, timeout=30)
        if r.status_code == 429:
            st.session_state.error = (
                "❌ **Gemini free‑tier quota exhausted** for today.\n\n"
                "Wait 24 h, create a new API key, or enable billing."
            )
            return False
    except Exception as exc:
        log.warning("[streamlit] Gemini quota check failed: %s", exc)

    st.session_state.preflight_done = True
    return True


def _run_generation(creative_direction: str):
    """Run the generation crew and extract image + caption."""
    from crew import build_generation_crew
    from utils.review import extract_image_and_caption

    gen_crew = build_generation_crew()
    gen_result = gen_crew.kickoff(
        inputs={"creative_direction": creative_direction}
    )
    log.info("[streamlit] Generation crew finished")

    image_path, caption = extract_image_and_caption(gen_result)
    return image_path, caption


def _run_posting(image_path: str, caption: str):
    """Run the posting crew."""
    from crew import build_posting_crew

    post_crew = build_posting_crew(image_path, caption)
    result = post_crew.kickoff()
    log.info("[streamlit] Posting crew finished")
    return str(result)


# ── UI ────────────────────────────────────────────────────────────────

st.title("🚀 Genfluence")
st.caption("AI Fitness Influencer Pipeline — powered by CrewAI + Gemini")

# Show any persistent error
if st.session_state.error:
    st.error(st.session_state.error)
    if st.button("🔄 Clear Error & Restart"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 1 — Creative Direction Input
# ═══════════════════════════════════════════════════════════════════════
if st.session_state.phase == "input":
    st.markdown("### 🎯 Creative Direction")
    st.markdown(
        "Describe the vibe, setting, outfit, mood, caption tone — anything!\n\n"
        "**Examples:**\n"
        '- *"Outdoor sunrise yoga on a mountain, peaceful and empowering"*\n'
        '- *"Intense gym workout, dark moody lighting, motivational caption"*\n'
        '- *"Beach run in summer sportswear, fun and energetic vibes"*'
    )

    direction = st.text_area(
        "Your direction",
        value=st.session_state.creative_direction,
        placeholder="Describe your vision for today's post…",
        height=120,
    )

    if st.button("✨ Generate Post", type="primary", use_container_width=True):
        creative_direction = direction.strip()
        if not creative_direction:
            creative_direction = (
                "Trending fitness content – choose the best idea based on research"
            )
        st.session_state.creative_direction = creative_direction
        st.session_state.attempt = 0
        st.session_state.error = None
        log.info("[streamlit] Direction: %s", creative_direction)

        # ── Pre‑flight (only once per session) ────────────────────────
        if not st.session_state.preflight_done:
            with st.spinner("🔐 Running pre‑flight checks (Instagram + Gemini)…"):
                if not _preflight_checks():
                    st.rerun()

        # ── Generation ────────────────────────────────────────────────
        st.session_state.attempt += 1
        attempt = st.session_state.attempt
        max_a = st.session_state.max_attempts

        with st.spinner(
            f"🎨 Generating image + caption (attempt {attempt}/{max_a})… "
            "This may take a couple of minutes."
        ):
            try:
                image_path, caption = _run_generation(creative_direction)
            except Exception as exc:
                st.session_state.error = f"❌ **Generation failed:** {exc}"
                log.error("[streamlit] Generation error: %s", exc)
                st.rerun()

        if not image_path:
            st.session_state.error = (
                "❌ Could not locate the generated image. "
                "Check the `output/` folder and logs."
            )
            st.rerun()
        if not caption:
            st.session_state.error = (
                "❌ Could not extract a caption from the crew output."
            )
            st.rerun()

        st.session_state.image_path = image_path
        st.session_state.caption = caption
        st.session_state.phase = "review"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2 — Review
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "review":
    st.markdown("### 👁️ Review Before Posting")

    attempt = st.session_state.attempt
    max_a = st.session_state.max_attempts
    st.info(f"Attempt **{attempt}** of **{max_a}**")

    # ── Show image ────────────────────────────────────────────────────
    img_path = Path(st.session_state.image_path)
    if img_path.exists():
        st.image(str(img_path), caption="Generated Image", use_container_width=True)
    else:
        st.warning(f"Image not found at `{img_path}`")

    # ── Show caption (editable) ───────────────────────────────────────
    st.markdown("**📝 Caption + Hashtags**")
    edited_caption = st.text_area(
        "Edit caption if needed",
        value=st.session_state.caption,
        height=180,
        label_visibility="collapsed",
    )
    st.session_state.caption = edited_caption

    # ── Action buttons ────────────────────────────────────────────────
    col_post, col_regen = st.columns(2)

    with col_post:
        post_clicked = st.button(
            "✅ Post to Instagram",
            type="primary",
            use_container_width=True,
        )

    with col_regen:
        regen_clicked = st.button(
            "🔄 Regenerate",
            use_container_width=True,
        )

    if post_clicked:
        from config import INSTAGRAM_USERNAME

        if not INSTAGRAM_USERNAME:
            st.warning(
                "⚠️ `INSTAGRAM_USERNAME` not set — posting skipped.\n\n"
                f"📸 Image saved at: `{st.session_state.image_path}`"
            )
            st.session_state.phase = "done"
            st.session_state.post_result = "Posting skipped (no IG credentials)"
            st.rerun()

        st.session_state.phase = "posting"
        st.rerun()

    if regen_clicked:
        if st.session_state.attempt >= st.session_state.max_attempts:
            st.session_state.error = (
                f"❌ Reached maximum regeneration attempts "
                f"({st.session_state.max_attempts}). Try again later."
            )
            st.rerun()

        st.session_state.attempt += 1
        attempt = st.session_state.attempt
        max_a = st.session_state.max_attempts
        log.info("[streamlit] Regenerating – attempt %d/%d", attempt, max_a)

        with st.spinner(
            f"🔄 Regenerating (attempt {attempt}/{max_a})…"
        ):
            try:
                image_path, caption = _run_generation(
                    st.session_state.creative_direction
                )
            except Exception as exc:
                st.session_state.error = f"❌ **Regeneration failed:** {exc}"
                st.rerun()

        if not image_path or not caption:
            st.session_state.error = (
                "❌ Could not extract image or caption after regeneration."
            )
            st.rerun()

        st.session_state.image_path = image_path
        st.session_state.caption = caption
        st.session_state.phase = "review"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 3 — Posting
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "posting":
    st.markdown("### 📸 Posting to Instagram…")

    with st.spinner("Uploading photo + caption to Instagram…"):
        try:
            result = _run_posting(
                st.session_state.image_path,
                st.session_state.caption,
            )
            st.session_state.post_result = result
            st.session_state.phase = "done"
            log.info("[streamlit] Post result: %s", result)
        except Exception as exc:
            st.session_state.error = f"❌ **Posting failed:** {exc}"
            log.error("[streamlit] Posting error: %s", exc)

    st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 4 — Done
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "done":
    st.markdown("### ✅ Pipeline Complete!")
    st.balloons()

    # Show final image + caption
    img_path = Path(st.session_state.image_path)
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)

    st.markdown("**Caption:**")
    st.text(st.session_state.caption)

    if st.session_state.post_result:
        st.success(st.session_state.post_result)

    st.divider()
    if st.button("🚀 Create Another Post", use_container_width=True):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()
