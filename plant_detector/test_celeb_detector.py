# test_celebrity_detector.py

import os
import sys
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import your detector
from celeb_detector import CelebrityDetector

def test_celebrity_detection(image_path):
    """
    Test the celebrity detector with a local image file
    """
    print(f"Testing with image: {image_path}")
    print("=" * 50)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at '{image_path}'")
        return
    
    # Load the image
    image = Image.open(image_path)
    
    # Convert to bytes
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Initialize detector
    detector = CelebrityDetector()
    
    # Run detection
    print("Analyzing image...")
    result, name, face_detected = detector.identify(image_bytes)
    
    # Display results
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Face Detected: {face_detected}")
    print(f"Celebrity Name: {name}")
    print("\nFull Analysis:")
    print("-" * 50)
    print(result)
    print("=" * 50)
    
    # Save results to file
    output_file = "celebrity_analysis_output.txt"
    with open(output_file, "w") as f:
        f.write(f"Image: {image_path}\n")
        f.write(f"Face Detected: {face_detected}\n")
        f.write(f"Celebrity Name: {name}\n\n")
        f.write("Full Analysis:\n")
        f.write("-" * 50 + "\n")
        f.write(result)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    # Check if image path provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test image
        image_path = "test_images/celebrity_photo.jpg"
    
    test_celebrity_detection(image_path)
