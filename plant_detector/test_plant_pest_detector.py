# test_plant_pest_detector.py

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

def test_plant_pest_detection(image_path):
    """
    Test the plant/pest detector with a local image file
    """
    print(f"Testing with image: {image_path}")
    print("=" * 60)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at '{image_path}'")
        return
    
    # Load the image
    try:
        image = Image.open(image_path)
        print(f"Image loaded: {image.size[0]}x{image.size[1]} pixels")
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    # Convert to bytes
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Initialize detector
    try:
        detector = PlantPestDetector()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GROQ_API_KEY in your .env file")
        return
    
    # Run detection
    print("Analyzing image...")
    result, subject_type, primary_id = detector.identify(image_bytes)
    
    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Subject Type: {subject_type}")
    print(f"Primary Identification: {primary_id}")
    print("\nFull Analysis:")
    print("-" * 60)
    print(result)
    print("=" * 60)
    
    # Save results to file
    output_file = "plant_pest_analysis_output.txt"
    with open(output_file, "w") as f:
        f.write(f"Image: {image_path}\n")
        f.write(f"Subject Type: {subject_type}\n")
        f.write(f"Primary Identification: {primary_id}\n\n")
        f.write("Full Analysis:\n")
        f.write("-" * 60 + "\n")
        f.write(result)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    # Check if image path provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = "test_images/plant_leaf.jpg"
    
    test_plant_pest_detection(image_path)
