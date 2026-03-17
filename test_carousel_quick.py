"""
Quick carousel post test - finds images in output/ and posts them immediately.
Useful for quick validation of carousel posting functionality.

Run: python test_carousel_quick.py
"""
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).resolve().parent))

from logger import log
from utils.instagram_tool import carousel_upload, preflight_login
from config import OUTPUT_DIR

RANDOM_CAPTIONS = [
    "💪 Lucknowi Ghar Ki Mashal: Workout Challenge! Your home is your gym! Small changes, BIG results. 🔥 #GharKiMashal #FitnessChallenge #HomeWorkout #FitnessCommunity",
    "🏋️‍♀️ Challenge Accepted? Transform your space, transform your body. Let's GO! 🚀 #GharKiMashal #FitnessGoals #HomeFitness #WorkoutChallenge",
    "✨ From couch to GOALS! Your living room is your personal fitness studio. 💪🔥 #GharKiMashal #FitnessJourney #HomeGym #FitnessCommunity",
    "🎯 You don't need a fancy gym. You need consistency & motivation. Let's make fitness FUN! 👇 #HomeWorkout #FitnessChallenge #GharKiMashal #MotivationMonday",
    "🌟 Your body is your first home. These moves are GAME CHANGERS. Ready for ghar ki mashal? 🔥💪 #FitnessCommunity #HealthyLiving #FitnessMotivation",
]

def main():
    print("\n" + "="*70)
    print("🚀 QUICK CAROUSEL POST TEST")
    print("="*70)
    
    # Find images
    output_path = Path(OUTPUT_DIR)
    images = sorted(list(output_path.glob("*.png")) + 
                   list(output_path.glob("*.jpg")) + 
                   list(output_path.glob("*.jpeg")))
    
    if not images:
        print("❌ No images found in output/ directory")
        print("   Please generate carousel images first using the Streamlit app.")
        sys.exit(1)
    
    # Select up to 5 most recent images (typical carousel size)
    selected = images[-5:] if len(images) >= 5 else images
    
    print(f"\n📸 Found {len(images)} images, using {len(selected)} for carousel:")
    for img in selected:
        print(f"   ✅ {img.name}")
    
    # Random caption
    caption = random.choice(RANDOM_CAPTIONS)
    print(f"\n📝 Caption:")
    print(f"   {caption[:120]}...")
    
    # Preflight
    print(f"\n🔐 Checking Instagram credentials...")
    try:
        preflight_login()
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        sys.exit(1)
    
    # Post
    print(f"\n⏳ Posting carousel ({len(selected)} slides) to Instagram...")
    result = carousel_upload([str(img) for img in selected], caption)
    
    print("\n" + "="*70)
    print("📊 RESULT")
    print("="*70)
    print(result)
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
