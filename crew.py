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
from agents.influencer_persona import create_influencer_persona
log.info("All agents loaded")

# ── Task factories ────────────────────────────────────────────────────
from tasks.research_task import create_research_task
from tasks.prompt_task import create_prompt_task
from tasks.generate_image_task import create_generate_image_task
from tasks.caption_hashtag_task import create_caption_hashtag_task
from tasks.post_to_instagram_task import create_post_to_instagram_task
from tasks.influencer_strategy_task import create_influencer_strategy_task
from tasks.influencer_validation_task import create_influencer_validation_task


def build_generation_crew(influencer_profile: str = "") -> Crew:
    """Assemble the generation crew with influencer strategy + validation."""
    log.info("Building GENERATION crew – wiring tasks…")

    influencer_persona = create_influencer_persona(influencer_profile)

    # 1 → Influencer persona strategy brief
    strategy = create_influencer_strategy_task(influencer_persona)
    log.info("  Task 1/6  ✔  Influencer Strategy")

    # 2 → Research trending fitness content
    research = create_research_task(researcher, context=[strategy])
    log.info("  Task 2/6  ✔  Research")

    # 3 → Craft a Nano Banana image-generation prompt
    prompt = create_prompt_task(prompt_creator, context=[strategy, research])
    log.info("  Task 3/6  ✔  Prompt")

    # 4 → Generate the AI image (character-consistent)
    gen_image = create_generate_image_task(image_generator, context=[prompt])
    log.info("  Task 4/6  ✔  Image Gen")

    # 5 → Write caption + 5 viral hashtags
    caption = create_caption_hashtag_task(
        caption_creator, context=[strategy, research, prompt]
    )
    log.info("  Task 5/6  ✔  Caption + Hashtags")

    # 6 → Validate final output against selected influencer persona
    validate = create_influencer_validation_task(
        influencer_persona, context=[strategy, research, prompt, gen_image, caption]
    )
    log.info("  Task 6/6  ✔  Persona Validation")
    log.info("Generation crew built – 5 agents, 6 tasks, sequential process")

    return Crew(
        agents=[
            influencer_persona,
            researcher,
            prompt_creator,
            image_generator,
            caption_creator,
        ],
        tasks=[strategy, research, prompt, gen_image, caption, validate],
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
