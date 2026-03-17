"""Task: Generate final content package from selected idea + content type."""
from crewai import Task


def create_content_package_task(agent):
    return Task(
        description=(
            "Create final content output from selected idea and content type.\n\n"
            "INFLUENCER PROFILE:\n"
            ">>> {influencer_profile} <<<\n\n"
            "CONTENT TYPE: {content_format}\n"
            "SELECTED IDEA: {selected_idea}\n\n"
            "STRATEGY BRIEF:\n"
            ">>> {strategy_brief} <<<\n\n"
            "RESEARCH IDEAS SUMMARY:\n"
            ">>> {research_ideas} <<<\n\n"
            "Rules:\n"
            "- Be highly creative, bold, and scroll-stopping\n"
            "- Prioritize novelty: avoid generic fitness clichés\n"
            "- Add a strong hook and emotional payoff in every format\n"
            "- Keep storytelling coherent\n"
            "- Use exactly 5 hashtags\n"
            "- Output ONLY one of the exact formats below based on CONTENT TYPE\n\n"
            "If CONTENT TYPE = post, output exactly:\n"
            "CONTENT_TYPE: post\n"
            "IMAGE_PROMPT: <single detailed image prompt>\n"
            "CAPTION: <caption>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5\n\n"
            "If CONTENT TYPE = carousel, output exactly:\n"
            "CONTENT_TYPE: carousel\n"
            "SLIDE_1_PROMPT: <hook cover image prompt with text to be written over the image>\n"
            "SLIDE_2_PROMPT: <story step 2 image prompt with text to be written over the image>\n"
            "SLIDE_3_PROMPT: <story step 3 image prompt with text to be written over the image>\n"
            "SLIDE_4_PROMPT: <story step 4 image prompt with text to be written over the image>\n"
            "SLIDE_5_PROMPT: <story step 5 image prompt with text to be written over the image>\n"
            "CAPTION: <caption for carousel post>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5\n\n"
            "CAROUSEL TEXT OVERLAY EXAMPLES (forming a story sequence):\n"
            "Slide 1: \"GHAR KI MASHAL\" (YOUR HOME GYM)\n"
            "Slide 2: \"NO EXCUSES\" (NO EQUIPMENT NEEDED)\n"
            "Slide 3: \"PUSH HARDER\" (FEEL THE BURN)\n"
            "Slide 4: \"BE STRONGER\" (TRANSFORMATION TIME)\n"
            "Slide 5: \"YOU GOT THIS\" (JOIN THE CHALLENGE)\n\n"
            "Each text overlay should be SHORT but meaningful, creatively written over the image to draw attention, and form a cohesive story \n"
            "If CONTENT TYPE = reel, output exactly:\n"
            "CONTENT_TYPE: reel\n"
            "VIDEO_SCRIPT: <short script with hook, beats, and CTA>\n"
            "CAPTION: <reel caption>\n"
            "HASHTAGS: #tag1 #tag2 #tag3 #tag4 #tag5"
        ),
        expected_output=(
            "Strictly formatted content package for selected content type with prompt/script, "
            "caption, and exactly 5 hashtags."
        ),
        agent=agent,
    )
