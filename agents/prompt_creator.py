# agents/prompt_creator.py
from crewai import Agent
from config import GEMINI_LLM_MODEL

prompt_creator = Agent(
    name="Nano Banana Prompt Engineer",
    role="Prompt Engineer",
    goal=(
        "Create world-class, precise, natural-language prompts optimised "
        "for Nano Banana (Gemini Image Generation) to produce a "
        "face-consistent, trending fitness influencer photo."
    ),
    backstory=(
        "Expert in crafting clear, structured, creative-director-level "
        "prompts designed for AI image generation workflows – high-"
        "consistency characters, fitness scenes, and polished social "
        "media compositions."
    ),
    llm=GEMINI_LLM_MODEL,
    max_iter=3,
    max_retry_limit=1,
    allow_delegation=False,
    verbose=True,
)