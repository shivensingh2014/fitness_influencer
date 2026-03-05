"""Task: Create an engaging caption and 5 viral hashtags."""
from crewai import Task


def create_caption_hashtag_task(agent, context):
    return Task(
        description=(
            "INFLUENCER PROFILE: A real fitness and lifestyle influencer who "
            "travels the world, trains in iconic cities, and coaches online "
            "as an AI fitness coach.\n\n"
            "TODAY'S POST TYPE (randomly selected):\n"
            "{post_type_brief}\n\n"
            "CREATIVE DIRECTION FROM THE USER:\n"
            ">>> {creative_direction} <<<\n\n"
            "Based on the post type, creative direction, trend research, and "
            "image prompt (all in context), write:\n\n"
            "1. ONE short, authentic Instagram caption (1-3 sentences) that:\n"
            "   • Sounds like a REAL person, not a bot (warm, witty, relatable)\n"
            "   • Matches the tone for this post type (motivational for gym, "
            "     wanderlust for travel, cozy for wellness, fun for BTS, "
            "     educational for coaching tips)\n"
            "   • Hooks the viewer and encourages engagement\n"
            "   • Uses emojis sparingly but effectively\n"
            "   • May reference the city/location if it's a travel post\n"
            "2. Exactly 5 hashtags chosen for maximum reach and virality. "
            "   Mix broad tags (#fitness, #travel, #lifestyle) with niche "
            "   and trending tags relevant to the post type.\n\n"
            "Format your output EXACTLY like this:\n"
            "CAPTION: <your caption here>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5"
        ),
        expected_output=(
            "CAPTION: <engaging caption matching the post type>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5"
        ),
        agent=agent,
        context=context,
    )
