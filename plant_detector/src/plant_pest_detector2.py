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
        Two-stage analysis: Returns short summary + full detailed analysis
        Returns: (short_summary, full_analysis, subject_type, primary_id)
        """
        # Open image with PIL
        image = Image.open(BytesIO(image_bytes))
        
        # STEP 1: Generate SHORT SUMMARY
        short_prompt = """You are an agricultural AI expert. Analyze this image and provide a SHORT summary (2-3 sentences maximum).

Include ONLY:
1. What you detected (pest name or disease name)
2. Severity level (mild/moderate/severe)
3. One sentence: "Provide your zip code for location-specific details andtreatment recommendations."

Be concise and direct. No additional details."""

        # STEP 2: Generate FULL DETAILED ANALYSIS
        detailed_prompt = """You are an agricultural AI expert specializing in plant health and pest identification.

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
            # Generate short summary
            short_response = self.model.generate_content([short_prompt, image])
            short_summary = short_response.text.strip()
            
            # Generate full detailed analysis
            detailed_response = self.model.generate_content([detailed_prompt, image])
            full_analysis = detailed_response.text.strip()
            
            # Extract metadata from full analysis
            subject_type = self.extract_subject_type(full_analysis)
            primary_id = self.extract_primary_id(full_analysis)
            
            return short_summary, full_analysis, subject_type, primary_id
            
        except Exception as e:
            error_msg = f"API request failed: {str(e)}"
            return error_msg, error_msg, "error", "Error"
    
    def extract_subject_type(self, content):
        """
        Determines if the detected subject is a plant or pest
        """
        if not content or content.startswith("Error") or content.startswith("API"):
            return "error"
        
        content_lower = content.lower()
        
        # Look for key indicators
        if "insect species:" in content_lower or "**insect species**" in content_lower:
            return "pest"
        elif "plant species:" in content_lower or "**plant species**" in content_lower:
            return "plant"
        elif "classification:" in content_lower and ("pest" in content_lower or "beneficial" in content_lower):
            return "pest"
        
        return "unknown"
    
    def extract_primary_id(self, content):
        """
        Extracts the main identification (plant species, disease name, or insect name)
        """
        if not content or content.startswith("Error") or content.startswith("API"):
            return "Error"
        
        lines = content.splitlines()
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Try to extract insect species first (priority for pests)
            if "insect species" in line_lower and ":" in line:
                insect = line.split(":", 1)[1].strip()
                # Clean up markdown and extra text
                insect = insect.replace("*", "").strip()
                if insect and insect.lower() not in ["unknown", "n/a", ""]:
                    return insect
            
            # Try to extract disease name (if plant is diseased)
            if "disease name" in line_lower and ":" in line:
                disease = line.split(":", 1)[1].strip()
                disease = disease.replace("*", "").strip()
                if disease and disease.lower() not in ["n/a", "none", "unknown", ""]:
                    return disease
            
            # Fallback: extract plant species
            if "plant species" in line_lower and ":" in line:
                species = line.split(":", 1)[1].strip()
                species = species.replace("*", "").strip()
                if species and species.lower() not in ["unknown", "n/a", ""]:
                    return species
        
        return "Unidentified"
