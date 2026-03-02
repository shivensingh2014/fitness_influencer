"""Task: Post the generated photo + caption to Instagram."""
from crewai import Task


def create_post_to_instagram_task(agent, context, image_path=None, caption=None):
    # When called with pre-approved image + caption (from the posting crew)
    if image_path and caption:
        description = (
            "Post the approved photo to Instagram.\n\n"
            f"Image path: {image_path}\n"
            f"Caption + hashtags:\n{caption}\n\n"
            "Steps:\n"
            "1. Call the 'post_to_instagram' tool with:\n"
            f"     image_path = {image_path}\n"
            "     caption    = the exact caption text provided above\n"
            "2. Return the result from the tool (post URL or error)."
        )
    else:
        # Original behaviour: extract from context
        description = (
            "Post the generated photo to Instagram.\n\n"
            "From context you have:\n"
            "  • The image file path (from the Image Generator's output)\n"
            "  • The caption and hashtags (from the Caption Creator's output)\n\n"
            "Steps:\n"
            "1. Extract the image_path from the Image Generator's output.\n"
            "2. Combine the caption and hashtags into ONE string:\n"
            "     <caption text>\\n\\n<hashtags>\n"
            "3. Call the 'post_to_instagram' tool with:\n"
            "     image_path = the extracted file path\n"
            "     caption    = the combined caption + hashtags string\n"
            "4. Return the result from the tool (post URL or error)."
        )

    return Task(
        description=description,
        expected_output="Confirmation message with the Instagram post URL.",
        agent=agent,
        context=context,
    )
