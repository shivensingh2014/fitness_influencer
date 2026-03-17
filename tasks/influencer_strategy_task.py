"""Task: Build an influencer-aligned strategy brief for downstream agents."""
from crewai import Task


def create_influencer_strategy_task(agent):
    return Task(
        description=(
            "You are the selected influencer's persona representative.\n\n"
            "INFLUENCER PROFILE:\n"
            ">>> {influencer_profile} <<<\n\n"
            "OUTPUT FORMAT: {content_format}\n"
            "\n"
            "Create a compact strategy brief that other agents must follow.\n"
            "Include audience-fit, tone, content angle, and constraints.\n\n"
            "CRITICAL RULES:\n"
            "- Output EXACTLY 5 lines only.\n"
            "- Do NOT output any extra sections, examples, explanations, markdown, images, captions, hashtags, separators, or notes.\n"
            "- Do NOT include blank lines.\n\n"
            "Output EXACTLY in this format:\n"
            "BRAND_INTENT: <1-2 lines>\n"
            "CONTENT_ANGLE: <1-2 lines>\n"
            "MUST_INCLUDE: <comma-separated points>\n"
            "MUST_AVOID: <comma-separated points>\n"
            "SUCCESS_CRITERIA: <3 bullet-like criteria in one line>"
        ),
        expected_output=(
            "BRAND_INTENT: ...\n"
            "CONTENT_ANGLE: ...\n"
            "MUST_INCLUDE: ...\n"
            "MUST_AVOID: ...\n"
            "SUCCESS_CRITERIA: ..."
        ),
        agent=agent,
    )
