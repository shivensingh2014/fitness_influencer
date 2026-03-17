# tasks/prompt_task.py
from crewai import Task


def create_prompt_task(agent, context):
    return Task(
        description=(
            "INFLUENCER PROFILE (selected by user):\n"
            ">>> {influencer_profile} <<<\n\n"
            "TODAY'S POST TYPE (randomly selected):\n"
            "{post_type_brief}\n\n"
            "OUTPUT FORMAT SELECTED BY USER: {content_format}\n"
            "(post = single hero frame, carousel = narrative sequence cover-like frame, "
            "reel = dynamic vertical key frame)\n\n"
            "Using the trend research (context) and post type, craft a single, "
            "highly detailed image-generation "
            "prompt optimised for Nano Banana (Gemini Image Generation). "
            "The prompt MUST:\n"
            "• Match the specific post type described above\n"
            "• Describe the EXACT scene, location details, pose, lighting, "
            "  camera angle, mood, and atmosphere\n"
            "• Specify outfit/athleisure details appropriate to the post type\n"
            "• Include background elements (people, architecture, nature, "
            "  equipment) that make the scene feel alive and real\n"
            "• Be written in natural language (no JSON, no code)\n"
            "• NOT describe the character's face – face consistency is handled "
            "  automatically by the reference image\n\n"
            "Output ONLY the prompt text, nothing else."
        ),
        expected_output=(
            "A single paragraph prompt (100-200 words) ready to be sent to "
            "the Nano Banana image generation API, matching the post type."
        ),
        agent=agent,
        context=context,
    )