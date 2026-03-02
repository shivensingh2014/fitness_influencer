# crew.py
"""
Genfluence Crew – full pipeline from trend research to Instagram post.
"""
import sys
from pathlib import Path

# Ensure the package root is importable when running crew.py directly
sys.path.insert(0, str(Path(__file__).parent))

from crewai import Crew, Process

from logger import log

log.info("Loading agents…")
# ── Agents ────────────────────────────────────────────────────────────
from agents.researcher import researcher
from agents.prompt_creator import prompt_creator
from agents.image_generator import image_generator
from agents.caption_creator import caption_creator
from agents.instagram_poster import instagram_poster
log.info("All 5 agents loaded")

# ── Task factories ────────────────────────────────────────────────────
from tasks.research_task import create_research_task
from tasks.prompt_task import create_prompt_task
from tasks.generate_image_task import create_generate_image_task
from tasks.caption_hashtag_task import create_caption_hashtag_task
from tasks.post_to_instagram_task import create_post_to_instagram_task


def build_generation_crew() -> Crew:
    """Assemble the generation crew (research → prompt → image → caption)."""
    log.info("Building GENERATION crew – wiring tasks…")

    # 1 → Research trending fitness content
    research = create_research_task(researcher)
    log.info("  Task 1/4  ✔  Research")

    # 2 → Craft a Nano Banana image-generation prompt
    prompt = create_prompt_task(prompt_creator, context=[research])
    log.info("  Task 2/4  ✔  Prompt")

    # 3 → Generate the AI image (character-consistent)
    gen_image = create_generate_image_task(image_generator, context=[prompt])
    log.info("  Task 3/4  ✔  Image Gen")

    # 4 → Write caption + 5 viral hashtags
    caption = create_caption_hashtag_task(
        caption_creator, context=[research, prompt]
    )
    log.info("  Task 4/4  ✔  Caption + Hashtags")
    log.info("Generation crew built – 4 agents, 4 tasks, sequential process")

    return Crew(
        agents=[researcher, prompt_creator, image_generator, caption_creator],
        tasks=[research, prompt, gen_image, caption],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )


def build_posting_crew(image_path: str, caption: str) -> Crew:
    """Assemble the posting crew with pre-resolved image path and caption."""
    log.info("Building POSTING crew…")

    post = create_post_to_instagram_task(
        instagram_poster,
        context=[],
        image_path=image_path,
        caption=caption,
    )
    log.info("  Task 1/1  ✔  Instagram Post")
    log.info("Posting crew built – 1 agent, 1 task")

    return Crew(
        agents=[instagram_poster],
        tasks=[post],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )


def build_crew() -> Crew:
    """Legacy: build the full 5-step crew (no review step)."""
    log.info("Building full crew – wiring tasks…")

    research = create_research_task(researcher)
    prompt = create_prompt_task(prompt_creator, context=[research])
    gen_image = create_generate_image_task(image_generator, context=[prompt])
    caption = create_caption_hashtag_task(
        caption_creator, context=[research, prompt]
    )
    post = create_post_to_instagram_task(
        instagram_poster, context=[gen_image, caption]
    )

    return Crew(
        agents=[
            researcher, prompt_creator, image_generator,
            caption_creator, instagram_poster,
        ],
        tasks=[research, prompt, gen_image, caption, post],
        process=Process.sequential,
        max_rpm=5,
        cache=True,
        verbose=True,
    )


if __name__ == "__main__":
    crew = build_generation_crew()
    result = crew.kickoff()
    print("\n=== GENERATION OUTPUT ===\n")
    print(result)
