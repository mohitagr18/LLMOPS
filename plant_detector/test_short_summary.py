# test_short_summary.py

import os
import sys
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import your detector
from plant_pest_detector2 import PlantPestDetector


def test_short_summary(image_path):
    """
    Test the new identify_with_summary method
    """
    print("\n" + "=" * 70)
    print("STEP 1.1 TEST: Short Summary Generation")
    print("=" * 70)
    print(f"Testing with image: {image_path}\n")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at '{image_path}'")
        return
    
    # Load the image
    try:
        image = Image.open(image_path)
        print(f"✓ Image loaded: {image.size[0]}x{image.size[1]} pixels")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return
    
    # Convert to bytes
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Initialize detector
    try:
        detector = PlantPestDetector()
        print("✓ PlantPestDetector initialized with Gemini 2.5 Flash")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GOOGLE_API_KEY in your .env file")
        return
    
    # Run detection with summary
    print("\n" + "-" * 70)
    print("Analyzing image (generating both short and full analysis)...")
    print("-" * 70)
    
    short_summary, full_analysis, subject_type, primary_id = detector.identify(image_bytes)
    
    # Display SHORT SUMMARY
    print("\n" + "=" * 70)
    print("📋 SHORT SUMMARY")
    print("=" * 70)
    print(short_summary)
    print("=" * 70)
    
    # Display METADATA
    print("\n" + "=" * 70)
    print("📊 EXTRACTED METADATA")
    print("=" * 70)
    print(f"Subject Type: {subject_type}")
    print(f"Primary ID: {primary_id}")
    print("=" * 70)
    
    # Display FULL ANALYSIS
    print("\n" + "=" * 70)
    print("📖 FULL DETAILED ANALYSIS")
    print("=" * 70)
    print(full_analysis)
    print("=" * 70)
    
    # Validation checks
    print("\n" + "=" * 70)
    print("✅ VALIDATION CHECKS")
    print("=" * 70)
    
    # Check 1: Short summary length
    word_count = len(short_summary.split())
    if word_count <= 100:
        print(f"✓ Short summary is concise: {word_count} words")
    else:
        print(f"⚠ Warning: Short summary is long: {word_count} words (target: <100)")
    
    # Check 2: Contains zip code prompt
    if "zip code" in short_summary.lower() or "location" in short_summary.lower():
        print("✓ Short summary prompts for location")
    else:
        print("⚠ Warning: Short summary doesn't prompt for location")
    
    # Check 3: Subject type detected
    if subject_type in ["plant", "pest"]:
        print(f"✓ Subject type correctly detected: {subject_type}")
    else:
        print(f"⚠ Warning: Subject type unclear: {subject_type}")
    
    # Check 4: Primary ID extracted
    if primary_id and primary_id != "Unidentified":
        print(f"✓ Primary identification extracted: {primary_id}")
    else:
        print(f"⚠ Warning: Could not extract primary ID: {primary_id}")
    
    # Check 5: Full analysis is detailed
    if len(full_analysis) > 500:
        print(f"✓ Full analysis is detailed: {len(full_analysis)} characters")
    else:
        print(f"⚠ Warning: Full analysis seems short: {len(full_analysis)} characters")
    
    print("=" * 70)
    
    # Save to file
    output_file = "step_1_1_test_output.txt"
    with open(output_file, "w") as f:
        f.write("STEP 1.1 TEST OUTPUT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Image: {image_path}\n")
        f.write(f"Subject Type: {subject_type}\n")
        f.write(f"Primary ID: {primary_id}\n\n")
        f.write("SHORT SUMMARY:\n")
        f.write("-" * 70 + "\n")
        f.write(short_summary + "\n\n")
        f.write("FULL ANALYSIS:\n")
        f.write("-" * 70 + "\n")
        f.write(full_analysis + "\n")
    
    print(f"\n✓ Results saved to: {output_file}")
    print("\n" + "=" * 70)
    print("STEP 1.1 TEST COMPLETE ✓")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Check if image path provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = "test_images/plant_leaf.jpg"
    
    test_short_summary(image_path)
