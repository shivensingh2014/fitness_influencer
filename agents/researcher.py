# agents/researcher.py
from crewai import Agent
from utils.google_search_tool import google_search
from config import GEMINI_LLM_MODEL

researcher = Agent(
    name="Fitness Trend Researcher",
    role="Researcher",
    goal="Find the best performing and trending fitness influencer content ideas.",
    backstory=(
        "You specialize in analyzing fitness trends, viral posts, "
        "and influencer engagement using internet search. "
        "Look for posts which have maximum views on Instagram and other portals."
    ),
    tools=[google_search],
    llm=GEMINI_LLM_MODEL,
    max_iter=3,               # limit reasoning loops (saves ~20 API calls)
    max_retry_limit=1,        # retry only once on failure
    allow_delegation=False,   # don't ask other agents (saves API calls)
    verbose=True,
)
