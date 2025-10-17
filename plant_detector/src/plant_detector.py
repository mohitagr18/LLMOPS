import os
import base64
import requests
from io import BytesIO
from PIL import Image

class PlantPestDetector:
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
    
    def identify(self, image_bytes):
        """
        Single-stage plant/pest detection and analysis
        No OpenCV needed - Llama 4 Maverick does everything
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
                            "text": """You are an agricultural AI expert specializing in plant health and pest identification.

Analyze this image and determine:

1. Is this a PLANT or an INSECT/PEST?

If it's a PLANT:
- **Plant Species**: [Identify if possible]
- **Health Status**: Healthy or Diseased
- **Disease Name**: [If diseased, provide specific name]
- **Symptoms Observed**: [Describe visible issues: spots, discoloration, wilting, etc.]
- **Severity Level**: Mild / Moderate / Severe
- **Recommended Treatments**: [List 2-3 treatment options]
- **Prevention Measures**: [How to prevent this issue]

If it's an INSECT/PEST:
- **Insect Species**: [Scientific and common name]
- **Classification**: Pest / Beneficial / Pollinator
- **Crops Affected**: [Which plants does it attack?]
- **Damage Description**: [What damage does it cause?]
- **Control Methods**: [List 2-3 control strategies]
- **Natural Predators**: [If applicable]

If the image shows something else or is unclear, respond with "Unable to identify - please provide a clearer image of a plant or insect."
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
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        response = requests.post(self.api_url, headers=headers, json=prompt)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            
            # Extract key information
            subject_type = self.extract_subject_type(result)
            primary_identification = self.extract_primary_id(result)
            
            return result, subject_type, primary_identification
        
        return "Error analyzing image", "unknown", ""
    
    def extract_subject_type(self, content):
        """
        Determines if the detected subject is a plant or pest
        """
        content_lower = content.lower()
        
        if "plant species:" in content_lower or "health status:" in content_lower:
            return "plant"
        elif "insect species:" in content_lower or "classification:" in content_lower:
            return "pest"
        
        return "unknown"
    
    def extract_primary_id(self, content):
        """
        Extracts the main identification (plant species or insect name)
        """
        for line in content.splitlines():
            line_lower = line.lower()
            
            # Try to extract plant species
            if line_lower.startswith("- **plant species**:"):
                return line.split(":", 1)[1].strip()
            
            # Try to extract disease name if plant is diseased
            if line_lower.startswith("- **disease name**:"):
                disease = line.split(":", 1)[1].strip()
                if disease and disease != "N/A":
                    return disease
            
            # Try to extract insect species
            if line_lower.startswith("- **insect species**:"):
                return line.split(":", 1)[1].strip()
        
        return "Unidentified"
