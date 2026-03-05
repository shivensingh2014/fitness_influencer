"""
Post Type Randomiser – picks a diverse content category each run
so the influencer feed never looks repetitive.

Usage:
    from utils.post_types import pick_random_post_type
    post_type = pick_random_post_type()   # returns a dict with 'name' + 'brief'
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from logger import log

# ── Diverse post categories ───────────────────────────────────────────
# Each entry has:
#   name  – short label shown to the user
#   brief – rich context injected into every agent/task prompt
POST_TYPES = [
    {
        "name": "🏙️ Travel Fitness – Iconic City Workout",
        "brief": (
            "POST TYPE: Travel Fitness – Iconic City Workout\n"
            "The influencer is working out in front of a world-famous landmark "
            "in a stunning city (e.g. Eiffel Tower, Dubai Marina, Tokyo streets, "
            "Santorini cliffs, New York skyline). The shot blends fitness with "
            "wanderlust – think yoga pose on a rooftop terrace, stretching by "
            "the Colosseum, or a HIIT set on a scenic bridge at golden hour."
        ),
    },
    {
        "name": "💪 Intense Gym Session – AI Coach Mode",
        "brief": (
            "POST TYPE: Intense Gym Session – AI Coach Mode\n"
            "The influencer is mid-workout in a modern, moody gym – heavy "
            "lifting, battle ropes, or a cable machine. Dramatic lighting "
            "(overhead spots, dark background). The vibe is motivational AI "
            "coach: powerful, disciplined, gritty. Think cinematic gym reels."
        ),
    },
    {
        "name": "🌄 Outdoor Adventure Fitness",
        "brief": (
            "POST TYPE: Outdoor Adventure Fitness\n"
            "The influencer is exercising in a breathtaking natural setting – "
            "mountain trail run, beach sprint, desert yoga, forest hike, or "
            "lakeside stretching. Epic landscape, golden/blue hour light, "
            "athletic wear that pops against nature. Conveys freedom and energy."
        ),
    },
    {
        "name": "🧘 Wellness & Morning Routine",
        "brief": (
            "POST TYPE: Wellness & Morning Routine\n"
            "Calm, aesthetic morning scene – sunrise meditation, journaling "
            "with a smoothie bowl, gentle yoga flow on a balcony, or a "
            "mindful walk. Soft warm tones, cozy-yet-fit lifestyle vibes. "
            "The message: balance, self-care, and starting the day right."
        ),
    },
    {
        "name": "🥗 Healthy Meal Prep & Nutrition",
        "brief": (
            "POST TYPE: Healthy Meal Prep & Nutrition\n"
            "The influencer in a beautiful kitchen or café – colourful meal "
            "prep spread, protein shake creation, or eating a vibrant salad "
            "bowl. Clean, bright, top-down or 45° food-meets-fitness aesthetic. "
            "Combines nutrition coaching with aspirational lifestyle."
        ),
    },
    {
        "name": "🔥 Transformation / Motivational",
        "brief": (
            "POST TYPE: Transformation / Motivational\n"
            "Powerful, emotional, inspirational shot – flexing after a PR, "
            "sweat-dripping determination face, or a triumphant finish-line "
            "moment. High-contrast dramatic lighting. The caption should be "
            "deeply motivational (progress > perfection, discipline = freedom)."
        ),
    },
    {
        "name": "✈️ Travel Day – Behind the Scenes",
        "brief": (
            "POST TYPE: Travel Day – Behind the Scenes\n"
            "Airport lounge vibes, window seat with clouds, arrival in a new "
            "city, dragging a suitcase through cobblestone streets, or a "
            "first-look balcony shot. Lifestyle content that shows the jet-"
            "setting side of being a travelling fitness influencer. Casual "
            "athleisure outfit, carry-on aesthetic."
        ),
    },
    {
        "name": "🏋️ Workout Tutorial – Coach Tip",
        "brief": (
            "POST TYPE: Workout Tutorial – Coach Tip\n"
            "The influencer demonstrating a specific exercise with perfect "
            "form – deadlift, plank variation, resistance band move, or a "
            "dynamic stretch. Shot from a helpful angle (side or ¾ view). "
            "Educational vibe: 'Your AI coach breaking down the move.' "
            "Clean gym or home-gym background."
        ),
    },
    {
        "name": "🌃 Night City Lifestyle",
        "brief": (
            "POST TYPE: Night City Lifestyle\n"
            "Evening/night-time urban scene – rooftop dinner after training, "
            "neon-lit city walk in athleisure, post-workout smoothie at a "
            "trendy bar, or a night run with city lights. Moody, cinematic "
            "tones (teal-orange, neon highlights). Shows the glamorous "
            "lifestyle side of fitness."
        ),
    },
    {
        "name": "🏖️ Beach / Pool Recovery Day",
        "brief": (
            "POST TYPE: Beach / Pool Recovery Day\n"
            "Rest-day content – lounging by an infinity pool, beach stretching, "
            "cold plunge, or foam rolling with an ocean backdrop. Relaxed but "
            "still fit. Bright, sun-kissed, vacation-wellness aesthetic. "
            "Message: recovery is part of the process."
        ),
    },
    {
        "name": "🤝 Partner / Group Workout",
        "brief": (
            "POST TYPE: Partner / Group Workout\n"
            "The influencer training with a friend, partner, or small group – "
            "buddy squats, high-fives after a set, group HIIT in a park, or "
            "partner yoga. Community-driven, fun, energetic. Shows the social, "
            "approachable side of fitness coaching."
        ),
    },
    {
        "name": "🛍️ Athleisure / Outfit of the Day",
        "brief": (
            "POST TYPE: Athleisure / Outfit of the Day\n"
            "Fashion-forward fitness look – posing in a new matching gym set, "
            "mirror selfie in a hotel gym, or street-style shot in athleisure "
            "against an urban backdrop. Focus on the outfit, colours, and how "
            "it looks during movement. Fitness-meets-fashion aesthetic."
        ),
    },
]


def pick_random_post_type() -> dict:
    """Return a randomly chosen post type dict with 'name' and 'brief'."""
    choice = random.choice(POST_TYPES)
    log.info("[post_types] Randomly selected: %s", choice["name"])
    return choice


def get_all_post_type_names() -> list[str]:
    """Return the list of all post type names (for UI display)."""
    return [pt["name"] for pt in POST_TYPES]
