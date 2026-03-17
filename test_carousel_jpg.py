"""
Test carousel post by converting PNG to JPG first (Instagram carousel prefers JPG).
"""
import sys
from pathlib import Path
import random
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from logger import log
from utils.instagram_tool import carousel_upload, preflight_login
from config import OUTPUT_DIR

RANDOM_CAPTIONS = [
    "💪 Lucknowi Ghar Ki Mashal: Workout Challenge! Your home is your gym! 🔥 #GharKiMashal #FitnessChallenge",
    "🏋️‍♀️ Challenge Accepted? Transform your space, transform your body! 🚀 #GharKiMashal #FitnessGoals",
    "✨ From couch to GOALS! Your living room is your fitness studio. 💪🔥 #GharKiMashal",
    "🎯 Small changes, BIG results! Let's make fitness FUN! 👇 #HomeWorkout #GharKiMashal",
    "🌟 Ready for the ghar ki mashal? 💪 #FitnessCommunity #HealthyLiving",
]

def main():
    print("\n" + "="*70)
    print("🚀 CAROUSEL TEST WITH JPG CONVERSION")
    print("="*70)
    
    # Find PNG images
    output_path = Path(OUTPUT_DIR)
    pngs = sorted(output_path.glob("generated_*.png"))
    
    if not pngs:
        print("❌ No generated images found")
        sys.exit(1)
    
    # Convert first 5 PNGs to JPG
    selected_pngs = pngs[-5:] if len(pngs) >= 5 else pngs
    jpg_paths = []
    
    print(f"\n🔄 Converting {len(selected_pngs)} PNGs to JPG...")
    for i, png_path in enumerate(selected_pngs, start=1):
        jpg_path = output_path / f"carousel_slide_{i}.jpg"
        try:
            img = Image.open(png_path)
            # Convert RGBA to RGB if needed
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(jpg_path, "JPEG", quality=90)
            jpg_paths.append(jpg_path)
            print(f"   ✅ {png_path.name} → {jpg_path.name}")
        except Exception as e:
            print(f"   ❌ Failed to convert {png_path.name}: {e}")
    
    if not jpg_paths:
        print("❌ Conversion failed")
        sys.exit(1)
    
    # Preflight
    print(f"\n🔐 Checking Instagram credentials...")
    try:
        preflight_login()
    except Exception as e:
        print(f"❌ Instagram login failed: {e}")
        sys.exit(1)
    
    # Random caption
    caption = random.choice(RANDOM_CAPTIONS)
    print(f"\n📝 Caption: {caption[:80]}...")
    
    # Post
    print(f"\n⏳ Posting carousel ({len(jpg_paths)} slides) to Instagram...")
    result = carousel_upload([str(p) for p in jpg_paths], caption)
    
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
