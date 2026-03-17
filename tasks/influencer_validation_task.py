"""Task: Validate generated content against influencer persona and strategy."""
from crewai import Task


def create_influencer_validation_task(agent, context):
    return Task(
        description=(
            "Validate final generation output against the selected influencer profile.\n\n"
            "INFLUENCER PROFILE:\n"
            ">>> {influencer_profile} <<<\n\n"
            "OUTPUT FORMAT: {content_format}\n"
            "POST TYPE: {post_type_brief}\n"
            "\n"
            "Use context from strategy + research + prompt + image path + caption.\n"
            "If output aligns well, mark PASS. If misaligned, mark REVISE and provide fixes.\n"
            "Always keep the image path and caption/hashtags visible for downstream parsing.\n\n"
            "Output EXACTLY in this format:\n"
            "VALIDATION: PASS or REVISE\n"
            "REASON: <short rationale>\n"
            "IMAGE_PATH: <absolute image path from context>\n"
            "CAPTION: <final approved or revised caption>\n"
            "HASHTAGS: <exactly 5 hashtags>\n"
            "IMPROVEMENTS: <concise next-step suggestions>"
        ),
        expected_output=(
            "Validation status with reason, image path, final CAPTION/HASHTAGS, and improvements."
        ),
        agent=agent,
        context=context,
    )
