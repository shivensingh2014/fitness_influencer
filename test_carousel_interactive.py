"""
Interactive carousel post test - provides a menu to test carousel posting.
Run: python test_carousel_interactive.py
"""
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).resolve().parent))

from logger import log
from utils.instagram_tool import carousel_upload, preflight_login
from config import OUTPUT_DIR

# Random fitness captions tailored for the Lucknowi Ghar Ki Mashal theme
CAPTIONS = [
    "💪 Lucknowi Ghar Ki Mashal: Workout Challenge! Your home is your gym! Small changes, BIG results. Tag a friend to join the #GharKiMashal! 🔥\n\n#FitnessChallenge #HomeWorkout #FitnessCommunity #GharKiMashal #FitnessGoals",
    
    "🏋️‍♀️ Challenge Accepted? Home workouts hit DIFFERENT! 💯 Transform your space, transform your body. Let's GO! 🚀\n\n#GharKiMashal #FitnessGoals #HomeFitness #WorkoutChallenge #StayActive",
    
    "✨ From couch to GOALS! This is what dedication looks like. Your living room is now your personal fitness studio. Join the movement! 💪🔥\n\n#GharKiMashal #FitnessJourney #HomeGym #TransformationStarts #FitnessCommunity",
    
    "🎯 Real talk: You don't need a fancy gym. You need consistency & motivation. Let's make fitness FUN again! Tag someone who needs this energy 👇\n\n#HomeWorkout #FitnessChallenge #Consistency #MotivationMonday #GharKiMashal",
    
    "🌟 Your body is your first home. Take care of it! These moves are GAME CHANGERS. Are you ready for the ghar ki mashal? 🔥💪\n\n#FitnessCommunity #HealthyLiving #WorkoutInspo #GharKiMashal #FitnessMotivation",
]

def list_available_images():
    """List PNG/JPG images in output directory."""
    output_path = Path(OUTPUT_DIR)
    if not output_path.exists():
        return []
    
    images = list(output_path.glob("*.png")) + list(output_path.glob("*.jpg")) + list(output_path.glob("*.jpeg"))
    return sorted(images)

def main():
    print("\n" + "="*70)
    print("🚀 CAROUSEL POST INTERACTIVE TEST")
    print("="*70)
    
    # Step 1: Preflight check
    print("\n🔐 Performing preflight check (Instagram login)...")
    try:
        preflight_login()
        print("✅ Instagram login successful!")
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        print("   Please check your INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env")
        sys.exit(1)
    
    # Step 2: Find available images
    print("\n🔍 Scanning for available images in output/ directory...")
    available_images = list_available_images()
    
    if not available_images:
        print("❌ No images found in output/ directory")
        print("   Generate some carousel images first using the Streamlit app")
        sys.exit(1)
    
    print(f"✅ Found {len(available_images)} image(s):")
    for i, img in enumerate(available_images, start=1):
        size_kb = img.stat().st_size / 1024
        print(f"   {i}. {img.name} ({size_kb:.1f} KB)")
    
    # Step 3: Select images
    print("\n📸 Select images to post as carousel:")
    print("   Enter image numbers separated by commas (e.g., 1,2,3)")
    print("   Or press Enter to select ALL images")
    
    user_input = input("👉 Your choice: ").strip()
    
    if user_input == "":
        selected_images = available_images
    else:
        try:
            indices = [int(x.strip()) - 1 for x in user_input.split(",")]
            selected_images = [available_images[i] for i in indices if 0 <= i < len(available_images)]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            sys.exit(1)
    
    if not selected_images:
        print("❌ No valid images selected")
        sys.exit(1)
    
    print(f"\n✅ Selected {len(selected_images)} image(s):")
    for img in selected_images:
        print(f"   - {img.name}")
    
    # Step 4: Choose caption
    print("\n📝 Choose a caption:")
    print("   1. Random caption (auto-selected)")
    print("   2. View caption options")
    print("   3. Use custom caption")
    
    caption_choice = input("👉 Your choice (default 1): ").strip() or "1"
    
    if caption_choice == "2":
        for i, cap in enumerate(CAPTIONS, start=1):
            print(f"\n--- Option {i} ---")
            print(cap[:100] + "..." if len(cap) > 100 else cap)
        caption_choice = input("👉 Select caption (1-5, default random): ").strip()
        if caption_choice.isdigit() and 1 <= int(caption_choice) <= len(CAPTIONS):
            caption = CAPTIONS[int(caption_choice) - 1]
        else:
            caption = random.choice(CAPTIONS)
    elif caption_choice == "3":
        caption = input("👉 Enter your caption: ").strip()
        if not caption:
            caption = random.choice(CAPTIONS)
    else:
        caption = random.choice(CAPTIONS)
    
    print(f"\n✅ Caption selected:")
    print(f"   {caption[:80]}...")
    
    # Step 5: Confirm and post
    print("\n" + "="*70)
    print(f"📊 POSTING SUMMARY")
    print("="*70)
    print(f"Format: CAROUSEL ({len(selected_images)} slides)")
    print(f"Images: {', '.join(img.name for img in selected_images)}")
    print(f"Caption: {caption[:100]}...")
    print("="*70)
    
    confirm = input("\n❓ Ready to post? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Cancelled")
        sys.exit(0)
    
    # Step 6: Upload
    print("\n⏳ Uploading carousel to Instagram...")
    print("   (This may take a minute...)")
    
    result = carousel_upload([str(img) for img in selected_images], caption)
    
    print("\n" + "="*70)
    print("✅ RESULT")
    print("="*70)
    print(result)
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
