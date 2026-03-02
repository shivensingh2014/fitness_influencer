"""Image Generator agent – creates photos via the Nano Banana API."""
from crewai import Agent
from utils.nano_banana_tool import generate_image
from config import GEMINI_LLM_MODEL

image_generator = Agent(
    name="Image Generator",
    role="AI Image Generator",
    goal=(
        "Generate a high-quality, character-consistent fitness influencer "
        "photo using the Nano Banana (Gemini Image Generation) API."
    ),
    backstory=(
        "You are an expert at translating creative prompts into stunning "
        "AI-generated images. You always ensure the character's face and "
        "identity remain perfectly consistent with the reference image."
    ),
    tools=[generate_image],
    llm=GEMINI_LLM_MODEL,
    max_iter=3,
    max_retry_limit=1,
    allow_delegation=False,
    verbose=True,
)
