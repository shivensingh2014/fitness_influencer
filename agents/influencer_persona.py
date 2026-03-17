"""Influencer Persona agent – defines brand voice and validates generated content."""
from crewai import Agent

from config import GEMINI_LLM_MODEL

def create_influencer_persona(influencer_profile: str = "") -> Agent:
    """Build an influencer persona agent with dynamic backstory from profile text."""
    profile_text = influencer_profile.strip()

    dynamic_backstory = (
        "You are the digital twin of the selected influencer profile. "
        "This is the exact influencer context you must embody:\n\n"
        f"{profile_text}\n\n"
        "Represent this person faithfully in style, audience fit, and content choices. "
        "Before creation, define what the post should achieve; after creation, "
        "quality-check image + caption fit and request revisions when misaligned."
    )

    if not profile_text:
        raise ValueError("Influencer profile text is empty. Cannot create persona agent.")

    return Agent(
        name="Influencer Persona Guardian",
        role="Influencer Persona Strategist & QA Reviewer",
        goal=(
            "Represent the selected influencer authentically, guide other agents on what "
            "content should be created, and validate whether final outputs align with "
            "the influencer's role, audience, tone, and goals."
        ),
        backstory=dynamic_backstory,
        llm=GEMINI_LLM_MODEL,
        max_iter=3,
        max_retry_limit=1,
        allow_delegation=False,
        verbose=True,
    )


# Backward-compatible default export for tests/imports.
influencer_persona = create_influencer_persona("Default influencer profile text")