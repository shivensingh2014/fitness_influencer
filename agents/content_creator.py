"""Content Creator agent – turns selected idea + content type into final content package."""
from crewai import Agent

from config import GEMINI_LLM_MODEL

content_creator = Agent(
    name="Creative Content Producer",
    role="Multi-format Content Creator",
    goal=(
        "Convert the selected research idea into highly creative, platform-ready content "
        "based on content type: post, carousel, or reel."
    ),
    backstory=(
        "You are a senior social content director who transforms trend ideas into "
        "compelling storytelling assets. You produce cinematic image prompts, strong "
        "captions, and strategic hashtags. For carousel you design narrative slide flow; "
        "for reels you create engaging short-form video scripts."
    ),
    llm=GEMINI_LLM_MODEL,
    max_iter=3,
    max_retry_limit=1,
    allow_delegation=False,
    verbose=True,
)
