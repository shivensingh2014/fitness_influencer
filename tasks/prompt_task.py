# tasks/prompt_task.py
from crewai import Task


def create_prompt_task(agent, context):
    return Task(
        description=(
            "Using the trending content research provided in context, craft "
            "a single, highly detailed image-generation prompt optimised for "
            "Nano Banana (Gemini Image Generation). The prompt MUST:\n"
            "• Describe the scene, pose, lighting, camera angle, and mood\n"
            "• Specify fitness attire and setting (gym, outdoor, studio, etc.)\n"
            "• Be written in natural language (no JSON, no code)\n"
            "• NOT describe the character's face – face consistency is handled "
            "  automatically by the reference image\n\n"
            "Output ONLY the prompt text, nothing else."
        ),
        expected_output=(
            "A single paragraph prompt (100-200 words) ready to be sent to "
            "the Nano Banana image generation API."
        ),
        agent=agent,
        context=context,
    )