# tasks/research_task.py
from crewai import Task


def create_research_task(agent, context=None):
    if context is None:
        context = []

    return Task(
        description=(
            "Use the INFLUENCER STRATEGY BRIEF from previous task context as your "
            "single source of truth.\n\n"
            "CONTENT TYPE: {content_format}\n"
            "This is CRITICAL for generating relevant ideas. Research ideas must be "
            "optimized for the selected format:\n"
            "• POST: Single high-impact image with strong caption. Focus on one powerful hook.\n"
            "• CAROUSEL: 5-slide narrative sequence. Each slide must advance a story. "
            "Ideas should have visual depth and multi-step progression.\n"
            "• REEL: 15-60 second video format. Ideas must have dynamic action, trend sounds, "
            "fast cuts, and strong retention hooks.\n\n"
            "TOOL CONTRACT (STRICT):\n"
            "1) Use ONLY the `google_search` tool for external information.\n"
            "2) Call it with EXACTLY one plain-text query string.\n"
            "3) Do NOT pass JSON or extra params such as mode, filters, language, region, or date.\n"
            "4) Keep each query short and focused (8-18 words).\n"
            "5) Use at most 3 tool calls total.\n"
            "6) If a call fails, retry once with a simpler query.\n"
            "7) Never output tool errors in final answer.\n\n"
            "Your job is to find current trending content opportunities that best "
            "match that strategy brief AND work well in the selected {content_format} format. "
            "Keep your reasoning generic and data-driven.\n\n"
            "Focus on:\n"
            "• Viral themes, hooks, and formats aligned to the strategy and {content_format}\n"
            "• Popular poses, settings, outfits, and compositions for {content_format}\n"
            "• Current seasonal, cultural, or location-based trend signals\n"
            "• Real influencer examples with high engagement in {content_format}\n\n"
            "Return a concise ranked list of the top 5 content ideas with evidence "
            "(engagement numbers, platform, example references). Rank ideas by fit "
            "against the strategy brief's MUST_INCLUDE, MUST_AVOID, and SUCCESS_CRITERIA, "
            "and suitability for {content_format}.\n\n"
            "Before finalizing, self-check:\n"
            "- Exactly 5 lines only\n"
            "- Each line starts with IDEA_1..IDEA_5\n"
            "- Each line is short title only (no explanations)\n\n"
            "Output format (strict):\n"
            "IDEA_1: <40 words idea detail >\n"
            "IDEA_2: <40 words idea detail >\n"
            "IDEA_3: <40 words idea detail >\n"
            "IDEA_4: <40 words idea detail >\n"
            "IDEA_5: <40 words idea detail >"
        ),
        expected_output=(
            "IDEA_1: <40 words idea detail >\n"
            "IDEA_2: <40 words idea detail >\n"
            "IDEA_3: <40 words idea detail >\n"
            "IDEA_4: <40 words idea detail >\n"
            "IDEA_5: <40 words idea detail >"
        ),
        agent=agent,
        context=context,
    )