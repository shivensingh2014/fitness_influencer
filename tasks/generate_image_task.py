"""Task: Generate an AI image via the Nano Banana API."""
from crewai import Task


def create_generate_image_task(agent, context):
    return Task(
        description=(
            "The creative director's vision: {creative_direction}\n\n"
            "Take the image-generation prompt from the Prompt Engineer's "
            "output (provided in context) and call the 'generate_image' tool "
            "with that exact prompt text. The prompt already incorporates "
            "the creative direction.\n\n"
            "The tool automatically:\n"
            "  1. Loads the base character reference image\n"
            "  2. Sends everything to the Nano Banana (Gemini) API\n"
            "  3. Saves the generated image locally\n\n"
            "Return ONLY the file path printed by the tool – nothing else."
        ),
        expected_output=(
            "The absolute file path to the generated image "
            "(e.g. C:/.../output/generated_20260227_150000.png)."
        ),
        agent=agent,
        context=context,
    )
