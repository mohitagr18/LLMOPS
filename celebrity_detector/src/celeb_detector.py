import os
import base64
import requests
from io import BytesIO
from PIL import Image

class CelebrityDetector:
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
    
    def identify(self, image_bytes):
        """
        Single-stage celebrity detection and identification
        No OpenCV needed - Llama 4 Maverick handles face detection AND recognition
        """
        encoded_image = base64.b64encode(image_bytes).decode()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are a celebrity recognition expert AI.

Analyze this image step by step:

STEP 1: Describe the visible facial features in detail
- Age range
- Facial structure
- Distinctive features

STEP 2: Identify the person
- If you recognize them as a celebrity, state their full name
- If you're uncertain, say "Uncertain" rather than guessing
- ONLY identify as a celebrity if you are confident (>80% sure)

STEP 3: Provide information in this format:
- **Confidence Level**: High/Medium/Low
- **Face Detected**: Yes/No
- **Full Name**: [Celebrity name or "Unknown" or "Uncertain"]
- **Profession**: [Their primary profession]
- **Nationality**: [Country of origin]
- **Famous For**: [What they are most known for]
- **Top Achievements**: [List 2-3 key accomplishments]

CRITICAL: If multiple celebrities might match, list them as alternatives:
- **Alternative Matches**: [Other possible identities if uncertain]
Be precise. Do NOT guess if uncertain.
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }
        
        response = requests.post(self.api_url, headers=headers, json=prompt)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            
            # Extract key information
            face_detected = self.extract_face_detection(result)
            name = self.extract_name(result)
            
            return result, name, face_detected
        
        return "Error analyzing image", "Unknown", False
    
    def extract_face_detection(self, content):
        """
        Determines if a face was detected in the image
        """
        for line in content.splitlines():
            if line.lower().startswith("- **face detected**:"):
                status = line.split(":", 1)[1].strip().lower()
                return status == "yes"
        
        return False
    
    def extract_name(self, content):
        """
        Extracts the celebrity's name from the response
        """
        for line in content.splitlines():
            if line.lower().startswith("- **full name**:"):
                name = line.split(":", 1)[1].strip()
                if name and name != "Unknown":
                    return name
        
        return "Unknown"
    
    def extract_profession(self, content):
        """
        Extracts the celebrity's profession (optional helper method)
        """
        for line in content.splitlines():
            if line.lower().startswith("- **profession**:"):
                return line.split(":", 1)[1].strip()
        
        return "Unknown"
