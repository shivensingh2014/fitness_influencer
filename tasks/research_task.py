# tasks/research_task.py
from crewai import Task


def create_research_task(agent):
    return Task(
        description=(
            "The creative director has given this direction for today's post:\n"
            ">>> {creative_direction} <<<\n\n"
            "With that direction in mind, search the internet for the latest "
            "trending fitness influencer content on Instagram, TikTok, and "
            "YouTube. Focus on:\n"
            "• Content that aligns with the creative direction above\n"
            "• Viral post themes and formats (reels, carousels, stories)\n"
            "• Popular fitness poses, settings, and aesthetics\n"
            "• Current seasonal or cultural trends in fitness\n\n"
            "Return a concise ranked list of the top 5 content ideas with "
            "evidence (engagement numbers, platform, example links). "
            "Rank ideas that match the creative direction higher."
        ),
        expected_output=(
            "A ranked list of 5 trending fitness content ideas, each with "
            "a brief description and supporting engagement data."
        ),
        agent=agent,
    )