import os
from io import BytesIO
from PIL import Image

# Set your Groq API key
os.environ["GROQ_API_KEY"] = "your_groq_api_key_here"

class MockFileWrapper:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
    
    def save(self, dst):
        self.image.save(dst, format='JPEG')

# Import and test
from your_module import CelebrityDetector

detector = CelebrityDetector()

# Test with a celebrity image
test_image = MockFileWrapper("celebrity_photo.jpg")

# Convert to bytes
buffer = BytesIO()
test_image.image.save(buffer, format='JPEG')
image_bytes = buffer.getvalue()

# Run detection
result, name, face_detected = detector.identify(image_bytes)

print(f"=== Celebrity Detection Results ===")
print(f"Face Detected: {face_detected}")
print(f"Celebrity Name: {name}")
print(f"\nFull Analysis:\n{result}")

# Save result to file
with open("celebrity_analysis.txt", "w") as f:
    f.write(f"Face Detected: {face_detected}\n")
    f.write(f"Celebrity Name: {name}\n\n")
    f.write(result)
