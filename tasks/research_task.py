# tasks/research_task.py
from crewai import Task


def create_research_task(agent):
    return Task(
        description=(
            "INFLUENCER PROFILE: You are researching for a real fitness and "
            "lifestyle influencer who travels the world, trains in iconic "
            "cities, and coaches online as an AI fitness coach. Their feed is "
            "diverse: workouts, travel, nutrition, wellness, athleisure, "
            "motivation, and behind-the-scenes lifestyle content.\n\n"
            "TODAY'S POST TYPE (randomly selected):\n"
            "{post_type_brief}\n\n"
            "CREATIVE DIRECTION FROM THE USER:\n"
            ">>> {creative_direction} <<<\n\n"
            "With the post type AND creative direction in mind, search the "
            "internet for the latest trending content that matches. Focus on:\n"
            "• Content that aligns with BOTH the post type and creative direction\n"
            "• Viral post themes, formats, and aesthetics for this category\n"
            "• Popular poses, settings, outfits, and compositions\n"
            "• Current seasonal, cultural, or location-based trends\n"
            "• Real influencer examples with high engagement\n\n"
            "Return a concise ranked list of the top 5 content ideas with "
            "evidence (engagement numbers, platform, example links). "
            "Rank ideas that match both the post type and creative direction higher."
        ),
        expected_output=(
            "A ranked list of 5 trending content ideas matching the post type, "
            "each with a brief description and supporting engagement data."
        ),
        agent=agent,
    )