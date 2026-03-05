"""
🚀 Genfluence – One-Click AI Fitness Influencer Pipeline

Run this script to:
  0. 🎯  Give your creative direction (guides every agent)
  0b.🎲  Randomly select a post type (travel, gym, wellness, etc.)
  1. 🔐  Verify Instagram login (fail-fast before burning API quota)
  2. Research trending fitness & lifestyle content
  3. Create an optimised Nano Banana image-generation prompt
  4. Generate a character-consistent AI photo
  5. Write an engaging caption + 5 viral hashtags
  6. 👁️  Review the image + caption (approve or regenerate)
  7. Post everything to Instagram automatically
"""
import sys
import traceback
from pathlib import Path

# Ensure the package root is on sys.path so all imports resolve
sys.path.insert(0, str(Path(__file__).parent))

from logger import log


def main():
    banner = """
╔══════════════════════════════════════════════════════════╗
║        🚀  GENFLUENCE – AI Influencer Pipeline          ║
╠══════════════════════════════════════════════════════════╣
║  0. 🎯  Your creative direction (guides the whole crew) ║
║  1. 🔐  Verify Instagram login (fail-fast)              ║
║  2. 🔍  Research trending fitness content               ║
║  3. ✏️   Create Nano Banana image prompt                 ║
║  4. 🎨  Generate AI photo (character-consistent)        ║
║  5. 📝  Write engaging caption + 5 viral hashtags       ║
║  6. 👁️   Review image + caption before posting           ║
║  7. 📸  Post to Instagram (only after your approval)    ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)
    log.info("═" * 50)
    log.info("Pipeline started")

    # ── Step 0: Creative Direction ────────────────────────────────────
    print("🎯  What's your vision for today's post?")
    print("   Describe the vibe, setting, outfit, mood, caption tone – anything!")
    print("   Examples:")
    print('     • "Outdoor sunrise yoga on a mountain, peaceful and empowering"')
    print('     • "Intense gym workout, dark moody lighting, motivational caption"')
    print('     • "Beach run in summer sportswear, fun and energetic vibes"')
    print()
    creative_direction = input("👉  Your direction: ").strip()

    if not creative_direction:
        creative_direction = "Trending fitness content – choose the best idea based on research"
        print(f"   (No direction given, using default: {creative_direction})")

    log.info("Creative direction: %s", creative_direction)
    print(f"\n✅  Direction locked: \"{creative_direction}\"\n")

    # ── Pick a random post type ───────────────────────────────────────
    from utils.post_types import pick_random_post_type
    post_type = pick_random_post_type()
    log.info("Post type: %s", post_type["name"])
    print(f"🎲  Post type: {post_type['name']}")
    print(f"   {post_type['brief'].split(chr(10))[1][:80]}…\n")

    # ── Pre-flight checks ─────────────────────────────────────────────
    from config import GEMINI_API_KEY, BASE_CHARACTER_IMAGE, INSTAGRAM_USERNAME

    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set")
        print("❌  GEMINI_API_KEY is not set. Copy .env.example → .env and fill it in.")
        sys.exit(1)

    char_img = Path(BASE_CHARACTER_IMAGE)
    if not char_img.is_absolute():
        char_img = Path(__file__).parent / char_img
    if not char_img.exists():
        log.error("Character image not found: %s", char_img)
        print(f"❌  Base character image not found at: {char_img}")
        print("   Place your character photo there and re-run.")
        sys.exit(1)
    log.info("Character image OK: %s (%.1f KB)", char_img, char_img.stat().st_size / 1024)

    # ── Step 0: Instagram login (fail-fast) ────────────────────────────
    ig_enabled = bool(INSTAGRAM_USERNAME)
    if not ig_enabled:
        log.warning("INSTAGRAM_USERNAME not set – posting will be skipped")
        print("⚠️  INSTAGRAM_USERNAME not set – the pipeline will run but skip posting.")
        print("   Set it in .env to enable auto-posting.\n")
    else:
        from utils.instagram_tool import preflight_login
        print(f"🔐  Logging into Instagram as @{INSTAGRAM_USERNAME}…")
        log.info("Instagram pre-flight login for @%s", INSTAGRAM_USERNAME)
        try:
            preflight_login()
            print("✅  Instagram login successful!\n")
        except Exception as _ig_exc:
            log.error("Instagram pre-flight login FAILED: %s", _ig_exc)
            print(f"\n❌  Instagram login FAILED: {_ig_exc}")
            print("\n   Possible fixes:")
            print("   1. Check INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env")
            print("   2. Open Instagram in a browser / phone and log in manually")
            print("      (clear any security challenge or 2FA prompt)")
            print("   3. Then re-run this pipeline.")
            sys.exit(1)

    # ── Verify Gemini API quota ────────────────────────────────────────
    import requests as _req
    log.info("Verifying Gemini API key & quota…")
    print("🔑  Verifying Gemini API key & quota…")
    _test_url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    )
    _test_body = {"contents": [{"parts": [{"text": "Say OK"}]}]}
    try:
        _r = _req.post(_test_url, json=_test_body, timeout=30)
        log.info("Quota check response: HTTP %s", _r.status_code)
        if _r.status_code == 429:
            _detail = _r.text[:500]
            log.error("QUOTA EXHAUSTED – HTTP 429\n%s", _detail)
            print("❌  Gemini free-tier quota EXHAUSTED for today.")
            print("   Options:")
            print("   1. Wait 24 h for the daily quota to reset.")
            print("   2. Create a NEW API key in a new GCP project at:")
            print("      https://aistudio.google.com/apikey")
            print("   3. Enable pay-as-you-go billing on your project.")
            sys.exit(1)
        elif _r.status_code != 200:
            _detail = _r.text[:500]
            log.warning("Quota check non-200: HTTP %s\n%s", _r.status_code, _detail)
            print(f"⚠️  Gemini API returned {_r.status_code}: {_r.text[:200]}")
            print("   The pipeline may fail. Double-check your GEMINI_API_KEY.")
    except Exception as _e:
        log.warning("Quota check failed: %s", _e)
        print(f"⚠️  Could not reach Gemini API: {_e}")

    log.info("Pre-flight checks passed")
    print("✅  Pre-flight checks passed. Kicking off the crew…\n")

    # ── Run: Generation → Review → Post loop ─────────────────────────
    from crew import build_generation_crew, build_posting_crew
    from utils.review import display_review, ask_approval, extract_image_and_caption

    MAX_ATTEMPTS = 5
    attempt = 0

    while attempt < MAX_ATTEMPTS:
        attempt += 1
        if attempt > 1:
            # Pick a NEW random post type on each regeneration for variety
            post_type = pick_random_post_type()
            print(f"\n🔄  Regenerating… (attempt {attempt}/{MAX_ATTEMPTS})")
            print(f"🎲  New post type: {post_type['name']}\n")
            log.info("Regeneration attempt %d/%d – post type: %s", attempt, MAX_ATTEMPTS, post_type["name"])

        # ── Phase 1: Generate image + caption ─────────────────────────
        try:
            gen_crew = build_generation_crew()
            gen_result = gen_crew.kickoff(
                inputs={
                    "creative_direction": creative_direction,
                    "post_type_brief": post_type["brief"],
                }
            )
            log.info("Generation phase completed")
        except Exception as exc:
            _handle_error(exc)
            sys.exit(1)

        # ── Phase 2: Review ───────────────────────────────────────────
        image_path, caption = extract_image_and_caption(gen_result)

        if not image_path:
            log.error("Could not find generated image in output")
            print("\n❌  Could not locate the generated image.")
            print("   Check the output/ folder and logs for details.")
            sys.exit(1)

        if not caption:
            log.error("Could not extract caption from output")
            print("\n❌  Could not extract a caption from the crew output.")
            sys.exit(1)

        display_review(image_path, caption)
        approved = ask_approval()

        if approved:
            # ── Phase 3: Post to Instagram ────────────────────────────
            if not ig_enabled:
                print("\n⚠️  INSTAGRAM_USERNAME not set – skipping posting.")
                print(f"   📸  Image saved at: {image_path}")
                print(f"   📝  Caption:\n{caption}")
                print("\n" + "=" * 58)
                print("✅  GENERATION COMPLETE (posting skipped)")
                print("=" * 58)
                sys.exit(0)

            try:
                post_crew = build_posting_crew(image_path, caption)
                post_result = post_crew.kickoff()
                log.info("Posting phase completed")
                print("\n" + "=" * 58)
                print("✅  PIPELINE COMPLETE!")
                print("=" * 58)
                print(post_result)
            except Exception as exc:
                _handle_error(exc)
                sys.exit(1)
            break  # Success – exit the loop
        else:
            log.info("User rejected – looping back to regenerate")
            print("\n🔄  Got it! Regenerating a fresh image and caption…")
            continue

    else:
        # Exhausted all attempts
        print(f"\n❌  Reached maximum regeneration attempts ({MAX_ATTEMPTS}).")
        print("   Try again later or adjust your configuration.")
        sys.exit(1)


def _handle_error(exc):
    """Print a human-friendly error diagnosis."""
    log.error("Pipeline FAILED: %s", exc)
    log.debug("Full traceback:\n%s", traceback.format_exc())

    err_str = str(exc)
    print("\n" + "=" * 58)
    print("❌  PIPELINE FAILED")
    print("=" * 58)

    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
        log.error("Root cause: Gemini API rate limit / quota exhausted")
        print("\n🔴 ROOT CAUSE: Gemini API rate limit / quota exhausted")
        print("   Your free-tier daily or per-minute quota has been hit.")
        print("   ➜ Wait for quota reset or create a new API key.")
    elif "401" in err_str or "UNAUTHENTICATED" in err_str:
        log.error("Root cause: Invalid or expired API key")
        print("\n🔴 ROOT CAUSE: Invalid or expired Gemini API key")
        print("   ➜ Regenerate at https://aistudio.google.com/apikey")
    elif "403" in err_str or "PERMISSION_DENIED" in err_str:
        log.error("Root cause: API key lacks permissions")
        print("\n🔴 ROOT CAUSE: API key lacks permissions for this model")
        print("   ➜ Enable the Generative Language API in your GCP project.")
    elif "timeout" in err_str.lower() or "timed out" in err_str.lower():
        log.error("Root cause: Network timeout")
        print("\n🔴 ROOT CAUSE: Network timeout contacting the API")
        print("   ➜ Check your internet connection and try again.")
    elif "Instagram" in err_str or "login" in err_str.lower():
        log.error("Root cause: Instagram login/post failure")
        print("\n🔴 ROOT CAUSE: Instagram login or posting failed")
        print("   ➜ Check credentials in .env; you may need to resolve a login challenge.")
    else:
        print(f"\n🔴 Error: {err_str[:300]}")

    print(f"\n📄 Full logs: output/genfluence.log")


if __name__ == "__main__":
    main()
