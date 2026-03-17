"""
Quick test script to post a carousel to Instagram with a random fitness caption.
Run: python test_carousel_post.py <image_path_1> <image_path_2> ... <image_path_n>
Example: python test_carousel_post.py output/image1.jpg output/image2.jpg output/image3.jpg
"""
import sys
from pathlib import Path
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from logger import log
from utils.instagram_tool import carousel_upload

# Random fitness captions
RANDOM_CAPTIONS = [
    "💪 Lucknowi Ghar Ki Mashal: Workout Challenge! Your home is your gym! Small changes, BIG results. Tag a friend to join the #GharKiMashal! 🔥 #FitnessChallenge #HomeWorkout #FitnessCommunity",
    "🏋️‍♀️ Challenge Accepted? Home workouts hit DIFFERENT! 💯 Transform your space, transform your body. Let's GO! 🚀 #GharKiMashal #FitnessGoals #HomeFitness",
    "✨ From couch to GOALS! This is what dedication looks like. Your living room is now your personal fitness studio. Join the movement! 💪🔥 #GharKiMashal #FitnessJourney",
    "🎯 Real talk: You don't need a fancy gym. You need consistency & motivation. Let's make fitness FUN again! Tag someone who needs this energy 👇 #HomeWorkout #FitnessChallenge",
    "🌟 Your body is your first home. Take care of it! These moves are GAME CHANGERS. Are you ready for the ghar ki mashal? 🔥💪 #FitnessCommunity #HealthyLiving",
]

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python test_carousel_post.py <image_path_1> <image_path_2> ...")
        print("Example: python test_carousel_post.py output/img1.jpg output/img2.jpg")
        sys.exit(1)
    
    image_paths = sys.argv[1:]
    
    # Validate image paths
    valid_paths = []
    for path_str in image_paths:
        p = Path(path_str)
        if not p.exists():
            print(f"❌ Image not found: {path_str}")
            continue
        valid_paths.append(p)
    
    if not valid_paths:
        print("❌ No valid image paths found")
        sys.exit(1)
    
    # Pick a random caption
    caption = random.choice(RANDOM_CAPTIONS)
    
    print("\n" + "="*60)
    print("🚀 CAROUSEL POST TEST")
    print("="*60)
    print(f"\n📸 Images to post ({len(valid_paths)}):")
    for i, p in enumerate(valid_paths, start=1):
        print(f"   {i}. {p.name} ({p.stat().st_size / 1024:.1f} KB)")
    
    print(f"\n📝 Caption:")
    print(f"   {caption}")
    
    print(f"\n🔄 Posting carousel to Instagram...")
    result = carousel_upload([str(p) for p in valid_paths], caption)
    
    print(f"\n✅ Result:")
    print(f"   {result}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
