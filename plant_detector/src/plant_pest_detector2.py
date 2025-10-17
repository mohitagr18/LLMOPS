# src/plant_pest_detector.py

import os
import google.generativeai as genai
from io import BytesIO
from PIL import Image


class PlantPestDetector:
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def identify(self, image_bytes):
        """
        Single-stage plant/pest detection and analysis using Gemini 2.5 Flash
        """
        # Open image with PIL
        image = Image.open(BytesIO(image_bytes))
        
        prompt = """You are an agricultural AI expert specializing in plant health and pest identification.

Analyze this image carefully and determine:

1. Is this a PLANT or an INSECT/PEST?

If it's a PLANT:
- **Plant Species**: [Identify if possible, including scientific name]
- **Health Status**: Healthy or Diseased
- **Disease Name**: [If diseased, provide specific name]
- **Symptoms Observed**: [Describe visible issues: spots, discoloration, wilting, lesions, etc.]
- **Severity Level**: Mild / Moderate / Severe
- **Recommended Treatments**: [List 2-3 treatment options with specific product types]
- **Prevention Measures**: [How to prevent this issue in the future]

If it's an INSECT/PEST:
- **Insect Species**: [Scientific and common name]
- **Classification**: Pest / Beneficial / Pollinator
- **Crops Affected**: [Which plants does it typically attack?]
- **Damage Description**: [What damage does it cause?]
- **Control Methods**: [List 2-3 control strategies]
- **Natural Predators**: [If applicable]

If the image shows something else or is unclear, respond with "Unable to identify - please provide a clearer image of a plant or insect."

Be specific and detailed in your analysis."""
        
        try:
            # Generate content with vision
            response = self.model.generate_content([prompt, image])
            result = response.text
            
            # Extract key information
            subject_type = self.extract_subject_type(result)
            primary_identification = self.extract_primary_id(result)
            
            return result, subject_type, primary_identification
            
        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            return error_msg, "error", ""
    
    def extract_subject_type(self, content):
        """
        Determines if the detected subject is a plant or pest
        """
        if not content or content.startswith("Error") or content.startswith("API"):
            return "error"
        
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
        if not content or content.startswith("Error") or content.startswith("API"):
            return "Error"
        
        for line in content.splitlines():
            line_lower = line.lower()
            
            # Try to extract plant species
            if line_lower.startswith("- **plant species**:") or line_lower.startswith("**plant species**:"):
                species = line.split(":", 1)[1].strip()
                if species and species.lower() != "unknown":
                    return species
            
            # Try to extract disease name if plant is diseased
            if line_lower.startswith("- **disease name**:") or line_lower.startswith("**disease name**:"):
                disease = line.split(":", 1)[1].strip()
                if disease and disease.lower() not in ["n/a", "none", "unknown", ""]:
                    return disease
            
            # Try to extract insect species
            if line_lower.startswith("- **insect species**:") or line_lower.startswith("**insect species**:"):
                insect = line.split(":", 1)[1].strip()
                if insect and insect.lower() != "unknown":
                    return insect
        
        return "Unidentified"
