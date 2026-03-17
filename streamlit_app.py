"""
🚀 Genfluence – Streamlit UI

Launch:
    cd fitness_crew
    streamlit run streamlit_app.py
"""
import sys
import time
import re
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
    "phase": "input",           # input → creative → generate → media → review → posting → done
    "selected_influencer": "",
    "influencer_profile": "",
    "influencer_confirmed": False,
    "content_setup_saved": False,
    "digital_twin_generated": False,
    "strategy_brief": "",
    "idea_results": "",
    "idea_options": [],
    "selected_idea": "",
    "content_package": "",
    "content_format": "post",
    "post_type_name": "",
    "post_type_brief": "",
    "image_path": "",
    "generated_image_paths": [],
    "video_script": "",
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


def _run_generation(
    post_type_brief: str,
    influencer_profile: str,
    content_format: str,
):
    """Run the generation crew and extract image + caption."""
    from crew import build_generation_crew
    from utils.review import extract_image_and_caption

    gen_crew = build_generation_crew(influencer_profile=influencer_profile)
    gen_result = gen_crew.kickoff(
        inputs={
            "post_type_brief": post_type_brief,
            "influencer_profile": influencer_profile,
            "content_format": content_format,
        }
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


def _run_content_package_generation(
    influencer_profile: str,
    content_format: str,
    selected_idea: str,
    strategy_brief: str,
    research_ideas: str,
) -> str:
    """Run dedicated content creator agent for post/carousel/reel output."""
    from crewai import Crew, Process

    from agents.content_creator import content_creator
    from tasks.content_package_task import create_content_package_task

    package_task = create_content_package_task(content_creator)

    content_crew = Crew(
        agents=[content_creator],
        tasks=[package_task],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )

    result = content_crew.kickoff(
        inputs={
            "influencer_profile": influencer_profile,
            "content_format": content_format,
            "selected_idea": selected_idea,
            "strategy_brief": strategy_brief,
            "research_ideas": research_ideas,
        }
    )
    return str(result)


def _extract_named_field(text: str, field_name: str) -> str:
    pattern = re.compile(rf"^{re.escape(field_name)}\s*:\s*(.+)$", flags=re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _generate_content_package_for_selected_idea() -> None:
    """Generate (or regenerate) content package for current selected idea."""
    package_output = _run_content_package_generation(
        influencer_profile=st.session_state.influencer_profile,
        content_format=st.session_state.content_format,
        selected_idea=st.session_state.selected_idea,
        strategy_brief=st.session_state.strategy_brief,
        research_ideas=st.session_state.idea_results,
    )

    st.session_state.content_package = package_output

    content_format = st.session_state.content_format.lower()
    caption = _extract_named_field(package_output, "CAPTION")
    hashtags = _extract_named_field(package_output, "HASHTAGS")
    video_script = _extract_named_field(package_output, "VIDEO_SCRIPT")
    st.session_state.caption = "\n\n".join([c for c in [caption, hashtags] if c]).strip()
    st.session_state.video_script = video_script
    st.session_state.image_path = ""
    st.session_state.generated_image_paths = []

    if content_format != "reel":
        st.session_state.video_script = ""


def _extract_numbered_prompts(text: str, prefix: str) -> list[str]:
    """Extract numbered prompt fields like SLIDE_1_PROMPT..SLIDE_N_PROMPT."""
    pattern = re.compile(
        rf"^({re.escape(prefix)}_(\d+)_PROMPT)\s*:\s*(.+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    matches: list[tuple[int, str]] = []
    for match in pattern.finditer(text):
        idx = int(match.group(2))
        prompt = match.group(3).strip()
        if prompt:
            matches.append((idx, prompt))

    return [prompt for _, prompt in sorted(matches, key=lambda item: item[0])]


def _extract_numbered_texts(text: str, prefix: str) -> list[str]:
    """Extract numbered text overlay fields like SLIDE_1_TEXT_OVERLAY..SLIDE_N_TEXT_OVERLAY."""
    pattern = re.compile(
        rf"^({re.escape(prefix)}_(\d+)_TEXT_OVERLAY)\s*:\s*(.+)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    matches: list[tuple[int, str]] = []
    for match in pattern.finditer(text):
        idx = int(match.group(2))
        text_overlay = match.group(3).strip()
        if text_overlay:
            matches.append((idx, text_overlay))

    return [text_overlay for _, text_overlay in sorted(matches, key=lambda item: item[0])]


def _generate_media_from_content_package(content_format: str, package_output: str) -> tuple[str, list[str], str]:
    """Generate media based on content type.

    Returns: (single_image_path, image_paths, video_script)
    """
    normalized = content_format.lower()

    if normalized == "reel":
        video_script = _extract_named_field(package_output, "VIDEO_SCRIPT")
        return "", [], video_script

    from utils.nano_banana_tool import generate_image

    if normalized == "post":
        image_prompt = _extract_named_field(package_output, "IMAGE_PROMPT")
        if not image_prompt:
            raise ValueError("IMAGE_PROMPT missing in content package.")

        img_result = generate_image.run(image_prompt)
        if "ERROR" in img_result.upper():
            raise RuntimeError(f"Image generation failed: {img_result}")
        return img_result, [img_result], ""

    if normalized == "carousel":
        slide_prompts = _extract_numbered_prompts(package_output, "SLIDE")
        slide_texts = _extract_numbered_texts(package_output, "SLIDE")
        
        if not slide_prompts:
            raise ValueError("No SLIDE_n_PROMPT fields found in content package.")

        from utils.text_overlay import add_carousel_overlays
        
        generated_paths: list[str] = []
        for i, prompt in enumerate(slide_prompts, start=1):
            img_result = generate_image.run(prompt)
            if "ERROR" in img_result.upper():
                raise RuntimeError(f"Slide {i} image generation failed: {img_result}")
            generated_paths.append(img_result)
        
        # Apply text overlays if available
        if slide_texts and len(slide_texts) == len(generated_paths):
            try:
                log.info("[streamlit] Applying text overlays to carousel slides...")
                generated_paths = add_carousel_overlays(generated_paths, slide_texts)
                log.info("[streamlit] Text overlays applied successfully")
            except Exception as exc:
                log.warning("[streamlit] Text overlay application failed: %s", exc)
                # Continue with original images if overlay fails

        first_path = generated_paths[0] if generated_paths else ""
        return first_path, generated_paths, ""

    raise ValueError(f"Unsupported content format: {content_format}")


def _initialize_digital_twin(
    influencer_profile: str,
    content_format: str,
    post_type_brief: str,
) -> str:
    """Run influencer strategy task and return strategy output for digital twin setup."""
    from crewai import Crew, Process

    from agents.influencer_persona import create_influencer_persona
    from tasks.influencer_strategy_task import create_influencer_strategy_task

    persona_agent = create_influencer_persona(influencer_profile)
    strategy_task = create_influencer_strategy_task(persona_agent)

    setup_crew = Crew(
        agents=[persona_agent],
        tasks=[strategy_task],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )

    result = setup_crew.kickoff(
        inputs={
            "influencer_profile": influencer_profile,
            "content_format": content_format,
            "post_type_brief": post_type_brief,
        }
    )
    return str(result)


def _run_research_ideas(
    strategy_brief: str,
    influencer_profile: str,
    content_format: str,
    post_type_brief: str,
) -> str:
    """Run only the researcher agent; its backstory is the strategy brief."""
    from crewai import Crew, Process

    from agents.researcher import create_researcher
    from tasks.research_task import create_research_task

    dynamic_researcher = create_researcher(strategy_brief)
    research_task = create_research_task(dynamic_researcher)

    research_crew = Crew(
        agents=[dynamic_researcher],
        tasks=[research_task],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )

    result = research_crew.kickoff(
        inputs={
            "influencer_profile": influencer_profile,
            "content_format": content_format,
            "post_type_brief": post_type_brief,
        }
    )
    return str(result)


def _extract_idea_options(idea_output: str) -> list[str]:
    """Parse research output into a clean list of idea titles for radio selection."""
    ideas: list[str] = []
    for raw_line in idea_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m = re.match(r"^IDEA_\d+\s*:\s*(.+)$", line, flags=re.IGNORECASE)
        if m:
            ideas.append(m.group(1).strip())
            continue

        m = re.match(r"^\d+[\).:-]\s*(.+)$", line)
        if m:
            ideas.append(m.group(1).strip())

    # Deduplicate while preserving order
    deduped: list[str] = []
    for idea in ideas:
        if idea and idea not in deduped:
            deduped.append(idea)

    return deduped


def _sanitize_strategy_brief(raw_output: str) -> str:
    """Keep only the 5 required strategy lines from first-agent output."""
    required_prefixes = [
        "BRAND_INTENT:",
        "CONTENT_ANGLE:",
        "MUST_INCLUDE:",
        "MUST_AVOID:",
        "SUCCESS_CRITERIA:",
    ]

    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    collected: list[str] = []

    for prefix in required_prefixes:
        matched_line = next(
            (line for line in lines if line.upper().startswith(prefix)),
            f"{prefix} (missing)",
        )
        collected.append(matched_line)

    return "\n".join(collected)


# ── UI ────────────────────────────────────────────────────────────────

st.title("🚀 Genfluence")
st.caption("AI Fitness Influencer Pipeline — powered by CrewAI + Gemini")

# ── Sidebar navigation ───────────────────────────────────────────────
_phase_to_page = {
    "input": "1) Setup",
    "creative": "2) Ideas",
    "generate": "3) Generate Post",
    "media": "4) Generate Media",
    "review": "5) Review",
    "posting": "6) Posting",
    "done": "7) Done",
}
_page_to_phase = {v: k for k, v in _phase_to_page.items()}

st.sidebar.markdown("## 🧭 Navigation")
current_page = _phase_to_page.get(st.session_state.phase, "1) Setup")
selected_page = st.sidebar.radio(
    "Go to page",
    options=list(_page_to_phase.keys()),
    index=list(_page_to_phase.keys()).index(current_page),
)

selected_phase = _page_to_phase.get(selected_page)
if selected_phase and selected_phase != st.session_state.phase:
    st.session_state.phase = selected_phase
    st.rerun()

# Show any persistent error
if st.session_state.error:
    st.error(st.session_state.error)
    if st.button("🔄 Clear Error & Restart"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 1 — Influencer + Content Type Setup
# ═══════════════════════════════════════════════════════════════════════
if st.session_state.phase == "input":
    from utils.influencer_context import load_influencer_profiles

    influencer_profiles = load_influencer_profiles()
    influencer_names = list(influencer_profiles.keys())
    if not influencer_names:
        st.session_state.error = (
            "❌ No influencer profiles found. Add .txt files in "
            "the `influencer_context/` folder."
        )
        st.rerun()

    default_name = st.session_state.selected_influencer
    if default_name not in influencer_names:
        default_name = influencer_names[0]

    st.markdown("### 🧍 Select Influencer")
    selected_influencer = st.selectbox(
        "Influencer profile",
        options=influencer_names,
        index=influencer_names.index(default_name),
        help="Profiles are loaded from influencer_context/*.txt",
    )

    if (
        st.session_state.selected_influencer
        and st.session_state.selected_influencer != selected_influencer
    ):
        st.session_state.influencer_confirmed = False
        st.session_state.content_setup_saved = False
        st.session_state.digital_twin_generated = False
        st.session_state.strategy_brief = ""
        st.session_state.idea_results = ""
        st.session_state.idea_options = []
        st.session_state.selected_idea = ""
        st.session_state.content_package = ""

    influencer_is_confirmed = (
        st.session_state.influencer_confirmed
        and st.session_state.selected_influencer == selected_influencer
    )

    if st.button("✅ Confirm Influencer", use_container_width=True):
        st.session_state.selected_influencer = selected_influencer
        st.session_state.influencer_profile = influencer_profiles[selected_influencer]
        st.session_state.influencer_confirmed = True
        influencer_is_confirmed = True
        log.info("[streamlit] Influencer confirmed: %s", selected_influencer)

    if influencer_is_confirmed:
        st.success(f"Influencer confirmed: **{selected_influencer}**")
    else:
        st.warning("Please confirm influencer before generating.")

    st.markdown("### 🎬 Content Type")
    selected_format = st.selectbox(
        "What do you want to generate?",
        options=["post", "carousel", "reel"],
        index=["post", "carousel", "reel"].index(
            st.session_state.content_format
            if st.session_state.content_format in {"post", "carousel", "reel"}
            else "post"
        ),
        help="Choose the format for this run.",
    )

    if st.button("💾 Save Influencer Profile and Content Type", use_container_width=True):
        if not influencer_is_confirmed:
            st.session_state.error = "❌ Please click **Confirm Influencer** first."
            st.rerun()

        from utils.post_types import pick_random_post_type

        post_type = pick_random_post_type()
        st.session_state.post_type_name = post_type["name"]
        st.session_state.post_type_brief = post_type["brief"]
        st.session_state.content_format = selected_format
        st.session_state.idea_results = ""
        st.session_state.idea_options = []
        st.session_state.selected_idea = ""
        st.session_state.content_package = ""
        st.session_state.error = None

        with st.spinner("🧠 Creating influencer digital twin..."):
            try:
                strategy_output = _initialize_digital_twin(
                    influencer_profile=st.session_state.influencer_profile,
                    content_format=st.session_state.content_format,
                    post_type_brief=st.session_state.post_type_brief,
                )
            except Exception as exc:
                st.session_state.error = f"❌ **Digital twin setup failed:** {exc}"
                log.error("[streamlit] Digital twin setup error: %s", exc)
                st.rerun()

        st.session_state.strategy_brief = _sanitize_strategy_brief(strategy_output)
        st.session_state.digital_twin_generated = True
        st.session_state.content_setup_saved = True
        log.info(
            "[streamlit] Setup saved | Influencer: %s | Format: %s | Post type: %s",
            st.session_state.selected_influencer,
            st.session_state.content_format,
            st.session_state.post_type_name,
        )
        st.success("✅ Digital twin generated.")

    if st.session_state.digital_twin_generated:
        st.info("Digital twin is generated and ready.")
        st.markdown("### 🧠 First Agent Output (Influencer Strategy)")
        st.text_area(
            "Strategy brief",
            value=st.session_state.strategy_brief,
            height=180,
            disabled=True,
        )


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2 — Creative Direction + Idea Generation
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "creative":
    st.markdown("### 💡 Generate Ideas")
    st.caption("Generate and select one idea before creating the post.")

    if st.button("💡 Generate Ideas", use_container_width=True):
        if not st.session_state.digital_twin_generated:
            st.session_state.error = "❌ Please complete page 1 setup first."
            st.rerun()

        with st.spinner("🔍 Running researcher to generate ideas..."):
            try:
                ideas_output = _run_research_ideas(
                    strategy_brief=st.session_state.strategy_brief,
                    influencer_profile=st.session_state.influencer_profile,
                    content_format=st.session_state.content_format,
                    post_type_brief=st.session_state.post_type_brief,
                )
            except Exception as exc:
                st.session_state.error = f"❌ **Idea generation failed:** {exc}"
                log.error("[streamlit] Idea generation error: %s", exc)
                st.rerun()

        st.session_state.idea_results = ideas_output
        st.session_state.idea_options = _extract_idea_options(ideas_output)
        if st.session_state.idea_options:
            st.session_state.selected_idea = st.session_state.idea_options[0]
        st.success("✅ Ideas generated.")

    if st.session_state.idea_results:
        st.markdown("### 💡 Research Ideas")
        if st.session_state.idea_options:
            default_index = 0
            if st.session_state.selected_idea in st.session_state.idea_options:
                default_index = st.session_state.idea_options.index(st.session_state.selected_idea)

            st.session_state.selected_idea = st.radio(
                "Select one idea",
                options=st.session_state.idea_options,
                index=default_index,
            )
        else:
            st.text_area(
                "Generated ideas",
                value=st.session_state.idea_results,
                height=220,
                disabled=True,
            )

    if st.button("➡️ Continue to Generate Post", type="primary", use_container_width=True):
        if not st.session_state.selected_idea:
            st.session_state.error = "❌ Please generate ideas and select one idea first."
            st.rerun()

        st.session_state.phase = "generate"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# PHASE 3 — Generate Post
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "generate":
    st.markdown("### ✨ Generate Post")
    st.info(
        f"Influencer: **{st.session_state.selected_influencer or 'Default'}**  ·  "
        f"Format: **{st.session_state.content_format.title()}**"
    )

    if st.session_state.selected_idea:
        st.markdown("**Selected Idea**")
        st.text(st.session_state.selected_idea)

    if st.session_state.content_package:
        st.markdown("### 📦 Generated Content Package")
        st.text_area(
            "Content package",
            value=st.session_state.content_package,
            height=260,
            disabled=True,
        )

    if st.button("✨ Generate Content Package", type="primary", use_container_width=True):
        if not st.session_state.content_setup_saved or not st.session_state.digital_twin_generated:
            st.session_state.error = (
                "❌ Please save influencer profile/content type and generate digital twin first."
            )
            st.rerun()

        if not st.session_state.selected_idea:
            st.session_state.error = "❌ Please select one idea before generating the post."
            st.rerun()

        st.session_state.attempt = 0
        st.session_state.error = None
        log.info(
            "[streamlit] Content package generation | Influencer: %s | Format: %s | Idea: %s",
            st.session_state.selected_influencer,
            st.session_state.content_format,
            st.session_state.selected_idea,
        )

        # ── Pre‑flight (only once per session) ────────────────────────
        if not st.session_state.preflight_done:
            with st.spinner("🔐 Running pre‑flight checks (Instagram + Gemini)…"):
                if not _preflight_checks():
                    st.rerun()

        with st.spinner("🧠 Generating content package..."):
            try:
                _generate_content_package_for_selected_idea()
            except Exception as exc:
                st.session_state.error = f"❌ **Content package generation failed:** {exc}"
                log.error("[streamlit] Content package generation error: %s", exc)
                st.rerun()

        st.success("✅ Content package generated. Review below, then approve or regenerate.")
        st.rerun()

    if st.session_state.content_package:
        col_approve, col_rerun = st.columns(2)

        with col_approve:
            if st.button("✅ Approve", type="primary", use_container_width=True):
                st.session_state.phase = "media"
                st.rerun()

        with col_rerun:
            if st.button("🔄 Regenerate Package", use_container_width=True):
                with st.spinner("🎯 Regenerating content package with high creativity..."):
                    try:
                        _generate_content_package_for_selected_idea()
                    except Exception as exc:
                        st.session_state.error = (
                            f"❌ **Content package regeneration failed:** {exc}"
                        )
                        log.error("[streamlit] Content package regeneration error: %s", exc)
                        st.rerun()

                st.success("✅ Fresh package generated.")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 4 — Generate Media
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "media":
    st.markdown("### 🖼️ Generate Media")
    content_format = st.session_state.content_format.lower()

    st.info(
        f"Influencer: **{st.session_state.selected_influencer or 'Default'}**  ·  "
        f"Format: **{st.session_state.content_format.title()}**"
    )

    if not st.session_state.content_package:
        st.session_state.error = "❌ Please generate and approve a content package first."
        st.session_state.phase = "generate"
        st.rerun()

    if content_format == "reel":
        video_script = st.session_state.video_script or _extract_named_field(
            st.session_state.content_package,
            "VIDEO_SCRIPT",
        )
        st.markdown("**🎬 Video Script**")
        st.text_area(
            "Reel script",
            value=video_script,
            height=220,
            disabled=True,
        )
        st.info("Reel selected: no image generation is performed.")

        if st.button("➡️ Continue to Review", type="primary", use_container_width=True):
            st.session_state.phase = "review"
            st.rerun()

    else:
        if st.button("🎨 Generate Images", type="primary", use_container_width=True):
            with st.spinner("🎨 Generating image(s) from approved content package..."):
                try:
                    image_path, image_paths, _ = _generate_media_from_content_package(
                        st.session_state.content_format,
                        st.session_state.content_package,
                    )
                except Exception as exc:
                    st.session_state.error = f"❌ **Media generation failed:** {exc}"
                    log.error("[streamlit] Media generation error: %s", exc)
                    st.rerun()

            st.session_state.image_path = image_path
            st.session_state.generated_image_paths = image_paths
            st.success("✅ Media generated successfully.")
            st.rerun()

        if st.session_state.generated_image_paths:
            if content_format == "post":
                st.image(st.session_state.generated_image_paths[0], caption="Generated Post Image", use_container_width=True)
            else:
                st.markdown("**Generated Carousel Slides**")
                for idx, image_path in enumerate(st.session_state.generated_image_paths, start=1):
                    st.image(image_path, caption=f"Slide {idx}", use_container_width=True)

            col_next, col_back = st.columns(2)
            with col_next:
                if st.button("➡️ Continue to Review", type="primary", use_container_width=True):
                    st.session_state.phase = "review"
                    st.rerun()
            with col_back:
                if st.button("⬅️ Back to Package", use_container_width=True):
                    st.session_state.phase = "generate"
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5 — Review
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "review":
    st.markdown("### 👁️ Review Before Posting")

    attempt = st.session_state.attempt
    max_a = st.session_state.max_attempts
    st.info(
        f"Attempt **{attempt}** of **{max_a}**  ·  "
        f"Post type: **{st.session_state.post_type_name}**  ·  "
        f"Influencer: **{st.session_state.selected_influencer or 'Default'}**  ·  "
        f"Format: **{st.session_state.content_format.title()}**"
    )

    # ── Show image / package ──────────────────────────────────────────
    if st.session_state.content_format.lower() == "post":
        img_path = Path(st.session_state.image_path)
        if st.session_state.image_path and img_path.exists():
            st.image(str(img_path), caption="Generated Image", use_container_width=True)
        else:
            st.warning("Image not available. Review the content package below.")
    elif st.session_state.content_format.lower() == "carousel":
        if st.session_state.generated_image_paths:
            st.markdown("**Generated Carousel Slides**")
            for idx, image_path in enumerate(st.session_state.generated_image_paths, start=1):
                st.image(image_path, caption=f"Slide {idx}", use_container_width=True)
        else:
            st.warning("Carousel images not generated yet.")
    else:
        st.info(
            "This format uses structured package output (carousel/reel). "
            "Review prompts/script below."
        )

    if st.session_state.content_package:
        st.markdown("**📦 Content Package**")
        st.text_area(
            "Generated package",
            value=st.session_state.content_package,
            height=260,
            disabled=True,
            key="review_content_package",
        )

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

        content_format = st.session_state.content_format.lower()

        # Check format support
        if content_format == "reel":
            st.warning(
                "⚠️ **Reel posting** not supported yet (video processing required)."
            )
            st.session_state.phase = "done"
            st.session_state.post_result = "Posting skipped (reel format not implemented)"
            st.rerun()

        if not INSTAGRAM_USERNAME:
            st.warning(
                "⚠️ `INSTAGRAM_USERNAME` not set — posting skipped.\n\n"
                f"📸 Images saved locally."
            )
            st.session_state.phase = "done"
            st.session_state.post_result = "Posting skipped (no IG credentials)"
            st.rerun()

        st.session_state.phase = "posting"
        st.rerun()

    if regen_clicked:
        st.session_state.phase = "generate"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PHASE 6 — Posting
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "posting":
    st.markdown("### 📸 Posting to Instagram…")

    content_format = st.session_state.content_format.lower()

    with st.spinner("Uploading to Instagram…"):
        try:
            if content_format == "carousel":
                if not st.session_state.generated_image_paths:
                    st.session_state.error = "❌ No carousel images available to post."
                    st.rerun()
                from utils.instagram_tool import carousel_upload
                result = carousel_upload(
                    st.session_state.generated_image_paths,
                    st.session_state.caption,
                )
            else:  # post format
                if not st.session_state.image_path:
                    st.session_state.error = "❌ No image available to post."
                    st.rerun()
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
# PHASE 7 — Done
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.phase == "done":
    st.markdown("### ✅ Pipeline Complete!")
    st.balloons()

    # Show final image + caption
    if st.session_state.content_format.lower() == "carousel":
        for idx, image_path in enumerate(st.session_state.generated_image_paths, start=1):
            if Path(image_path).exists():
                st.image(str(image_path), caption=f"Slide {idx}", use_container_width=True)
    else:
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
