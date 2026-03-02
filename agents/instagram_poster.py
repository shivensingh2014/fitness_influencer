"""Instagram Poster agent – publishes the final content to Instagram."""
from crewai import Agent
from utils.instagram_tool import post_to_instagram
from config import GEMINI_LLM_MODEL

instagram_poster = Agent(
    name="Instagram Poster",
    role="Social Media Publisher",
    goal=(
        "Post the generated photo to Instagram with the provided caption "
        "and hashtags. Confirm success and return the post URL."
    ),
    backstory=(
        "You handle the final mile – uploading polished content to Instagram. "
        "You combine the image path, caption, and hashtags into a single "
        "publish action and verify the post went live."
    ),
    tools=[post_to_instagram],
    llm=GEMINI_LLM_MODEL,
    max_iter=3,
    max_retry_limit=1,
    allow_delegation=False,
    verbose=True,
)
