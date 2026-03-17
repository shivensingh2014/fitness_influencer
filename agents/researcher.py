# agents/researcher.py
from crewai import Agent
from utils.google_search_tool import google_search
from config import GEMINI_LLM_MODEL

def create_researcher(backstory_override: str = "") -> Agent:
    """Build a researcher agent with optional runtime backstory override."""
    backstory = backstory_override.strip() or (
        "You are the research brain behind a top-tier fitness and lifestyle "
        "influencer who travels the world – training in iconic cities, coaching "
        "online as an AI fitness coach, and sharing wellness and travel content. "
        "You track viral trends across Instagram, TikTok, YouTube Shorts, and "
        "Pinterest for ALL content pillars: workouts, travel, food, fashion, "
        "motivation, and behind-the-scenes lifestyle. You look for posts with "
        "maximum engagement (saves, shares, comments) and fresh angles that "
        "keep the feed diverse and never repetitive."
    )

    return Agent(
        name="Lifestyle Trend Scout",
        role="Trend & Culture Researcher",
        goal=(
            "Discover the hottest trending content ideas across fitness, travel, "
            "lifestyle, and wellness that a globe-trotting influencer  "
            "would post. Identify viral trends with high engagement potential and fresh angles"
            "for a lifestyle influencer on Instagram, TikTok, YouTube Shorts, and Pinterest."
        ),
        backstory=(
            f"{backstory}\n\n"
            "Tool rule: when using google_search, pass only one plain text query string. "
            "Never send extra parameters like mode, filters, language, or JSON payloads."
        ),
        tools=[google_search],
        llm=GEMINI_LLM_MODEL,
        max_iter=3,               # limit reasoning loops (saves ~20 API calls)
        max_retry_limit=1,        # retry only once on failure
        allow_delegation=False,   # don't ask other agents (saves API calls)
        verbose=True,
    )


researcher = create_researcher()
