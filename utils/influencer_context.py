"""Helpers for loading influencer profile context files."""
from pathlib import Path

from config import INFLUENCER_CONTEXT_DIR
from logger import log


_DEFAULT_PROFILE = (
    "A real fitness and lifestyle influencer who creates authentic content "
    "around workouts, wellness, and daily routines for a broad audience."
)


def load_influencer_profiles() -> dict[str, str]:
    """
    Load influencer profiles from *.txt files in INFLUENCER_CONTEXT_DIR.

    Returns:
        A dict mapping influencer name -> profile text.
        If no files are found, returns {"Default": _DEFAULT_PROFILE}.
        Empty files are accepted and replaced with a minimal fallback profile.
    """
    context_dir = Path(INFLUENCER_CONTEXT_DIR)
    if not context_dir.exists():
        log.warning("[influencer_context] Directory missing: %s", context_dir)
        return {"Default": _DEFAULT_PROFILE}

    profiles: dict[str, str] = {}
    for file_path in sorted(context_dir.glob("*.txt")):
        influencer_name = file_path.stem.strip() or file_path.name

        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except Exception as exc:
            log.warning(
                "[influencer_context] Failed reading %s: %s", file_path, exc
            )
            continue

        if not content:
            content = (
                f"Influencer name: {influencer_name}. "
                "No detailed profile provided yet. Generate broadly relevant "
                "fitness and lifestyle content in an authentic tone."
            )

        profiles[influencer_name] = content

    if not profiles:
        log.warning(
            "[influencer_context] No influencer .txt files found in %s; using default",
            context_dir,
        )
        return {"Default": _DEFAULT_PROFILE}

    log.info("[influencer_context] Loaded %d influencer profile(s)", len(profiles))
    return profiles
