"""Task: Create an engaging caption and 5 viral hashtags."""
from crewai import Task


def create_caption_hashtag_task(agent, context):
    return Task(
        description=(
            "Based on the trend research and the image prompt (both provided "
            "in context), write:\n\n"
            "1. ONE short, engaging Instagram caption (1-3 sentences) that "
            "   hooks the viewer and encourages engagement (likes, comments, "
            "   saves, shares). Use emojis sparingly but effectively.\n"
            "2. Exactly 5 hashtags chosen for maximum reach and virality. "
            "   Mix broad reach tags with niche fitness tags.\n\n"
            "Format your output EXACTLY like this (so the next agent can "
            "parse it):\n"
            "CAPTION: <your caption here>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5"
        ),
        expected_output=(
            "CAPTION: <engaging caption text>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5"
        ),
        agent=agent,
        context=context,
    )
