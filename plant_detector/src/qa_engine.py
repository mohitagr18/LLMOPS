# src/qa_engine.py

import os
import google.generativeai as genai
from typing import Dict, Optional, List
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp_server'))
from amazon_tools import search_amazon_products


class AgriQAEngine:
    """
    QA Engine with infestation-level-aware recommendations
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Context storage
        self.pest_or_disease = None
        self.severity = None
        self.subject_type = None
        self.plant_type = None
        self.infestation_level = None
        self.location_context = None
        self.conversation_history = []
    
    def set_detection_context(self, pest_or_disease: str, severity: str, 
                             subject_type: str, plant_type: str = "Unknown",
                             infestation_level: str = "Unknown"):
        """Set detection context with infestation level"""
        self.pest_or_disease = pest_or_disease
        self.severity = severity
        self.subject_type = subject_type
        self.plant_type = plant_type
        self.infestation_level = infestation_level
    
    def set_location_context(self, weather_data: Dict, soil_data: Dict):
        """Set location context"""
        self.location_context = {
            "weather": weather_data,
            "soil": soil_data
        }
    
    def parse_user_input(self, user_text: str) -> Dict:
        """
        Parse user input to extract: plant/crop, zip code, infestation level
        """
        result = {
            "plant_type": None,
            "zipcode": None,
            "infestation_level": None
        }
        
        # Extract zip code (5 digits)
        zip_match = re.search(r'\b\d{5}\b', user_text)
        if zip_match:
            result["zipcode"] = zip_match.group()
        
        # Extract infestation level
        text_lower = user_text.lower()
        if "low" in text_lower:
            result["infestation_level"] = "low"
        elif "medium" in text_lower or "moderate" in text_lower:
            result["infestation_level"] = "medium"
        elif "high" in text_lower or "severe" in text_lower or "heavy" in text_lower:
            result["infestation_level"] = "high"
        
        # Extract plant type
        plant_text = re.sub(r'\b\d{5}\b', '', user_text)
        plant_text = re.sub(r'\b(low|medium|moderate|high|severe|heavy|infestation|level)\b', '', plant_text, flags=re.IGNORECASE)
        plant_text = plant_text.strip().strip(',').strip()
        
        if plant_text:
            result["plant_type"] = plant_text.title()
        
        return result
    
    def generate_initial_summary(self) -> Dict:
        """
        Generate initial response with context + detailed immediate assessment
        NO 3-day forecast here (only current weather)
        """
        if not self.pest_or_disease or not self.location_context:
            return {"error": "Missing context"}
        
        weather = self.location_context.get("weather", {})
        soil = self.location_context.get("soil", {})
        
        # Build weather summary (CURRENT ONLY - no 3-day forecast)
        weather_summary = "Weather data unavailable"
        if "error" not in weather:
            location = weather.get("location", {})
            current = weather.get("current", {})
            
            weather_summary = f"""📍 **{location.get('city')}, {location.get('state')}**
🌡️ Current: {current.get('temperature')}°{current.get('temperature_unit')}, {current.get('short_forecast')}
💨 Wind: {current.get('wind_speed')} {current.get('wind_direction')}"""
        
        # Build soil summary
        soil_summary = "Soil data unavailable"
        if "error" not in soil:
            soil_props = soil.get("soil_properties", {})
            soil_summary = f"""🪨 **Soil Type:** {soil_props.get('soil_name')}
📊 **Texture:** {soil_props.get('soil_texture')}
💧 **Drainage:** {soil_props.get('drainage_class')}
"""
            sand = soil_props.get('sand_percent')
            clay = soil_props.get('clay_percent')
            ph = soil_props.get('ph')
            
            if sand != "Not available":
                soil_summary += f"🏖️ **Sand:** {sand}%\n"
            if clay != "Not available":
                soil_summary += f"🧱 **Clay:** {clay}%\n"
            if ph != "Not available":
                soil_summary += f"🧪 **pH:** {ph}\n"
        
        # Generate MORE DETAILED immediate assessment
        infestation_note = f" (Infestation: {self.infestation_level})" if self.infestation_level != "Unknown" else ""
        
        context_text = f"""
DETECTED: {self.pest_or_disease}
SEVERITY: {self.severity}{infestation_note}
PLANT: {self.plant_type}
LOCATION: {weather.get('location', {}).get('city')}, {weather.get('current', {}).get('temperature')}°F
SOIL: {soil.get('soil_properties', {}).get('soil_texture')}
"""
        
        assessment_prompt = f"""You are an agricultural advisor. Provide a DETAILED immediate assessment (3-4 sentences).

{context_text}

Provide:
1. **Urgency:** [Immediate/Within 24hrs/Monitor closely/etc.]
2. **Risk Factor:** What specific risk this pest/disease poses to {self.plant_type} (e.g., "voracious feeders capable of rapid defoliation and significant yield loss")
3. One brief action recommendation

Format:
**Urgency:** [level]
**Risk Factor:** [specific risk to crop]
**Action:** [brief recommendation]

Keep it concise but MORE detailed than 2 sentences."""

        try:
            response = self.model.generate_content(assessment_prompt)
            immediate_assessment = response.text.strip()
        except:
            immediate_assessment = f"**Urgency:** Moderate\n**Risk Factor:** {self.pest_or_disease} can cause significant damage to {self.plant_type}.\n**Action:** Treatment recommended."
        
        # Updated menu options with option 5 (Detailed Report) and option 6 (Custom Question)
        menu_options = [
            "1️⃣ Treatment Recommendations (with product links)",
            "2️⃣ Detailed Soil Impact",
            "3️⃣ Weather-Based Timing",
            "4️⃣ Monitoring & Prevention",
            "5️⃣ Detailed Report (All recommendations)",
            "6️⃣ Ask Custom Question"
        ]
        
        return {
            "weather_summary": weather_summary,
            "soil_summary": soil_summary,
            "immediate_assessment": immediate_assessment,
            "menu_options": menu_options
        }
    
    def get_menu_options(self) -> List[str]:
        """Return menu options for display"""
        return [
            "1️⃣ Treatment Recommendations (with product links)",
            "2️⃣ Detailed Soil Impact",
            "3️⃣ Weather-Based Timing",
            "4️⃣ Monitoring & Prevention",
            "5️⃣ Detailed Report (All recommendations)",
            "6️⃣ Ask Custom Question"
        ]
    
    def answer_menu_selection(self, option: int) -> str:
        """
        Answer based on menu selection
        Keep responses to EXACTLY 2-3 paragraphs (except detailed report)
        """
        if not self.pest_or_disease or not self.location_context:
            return "Missing context. Please start over."
        
        weather = self.location_context.get("weather", {})
        soil = self.location_context.get("soil", {})
        
        # Build compact context
        location_temp = weather.get('current', {}).get('temperature')
        soil_texture = soil.get('soil_properties', {}).get('soil_texture')
        soil_drainage = soil.get('soil_properties', {}).get('drainage_class')
        
        context = f"""
ISSUE: {self.pest_or_disease} ({self.severity})
PLANT: {self.plant_type}
INFESTATION LEVEL: {self.infestation_level}
TEMP: {location_temp}°F
SOIL: {soil_texture}, {soil_drainage}
"""
        
        if option == 1:  # Treatment Recommendations
            if self.infestation_level == "Unknown":
                prompt = f"""{context}

Provide brief treatment recommendations for ALL THREE infestation levels.

For each level, recommend 2-3 SPECIFIC product types (e.g., "Bt insecticide", "Spinosad spray", "Neem oil concentrate").

Format:
**Low Infestation:**
- Manual removal (if applicable)
- Product types: [specific product type 1], [specific product type 2]

**Medium Infestation:**
- Product types: [specific product type 1], [specific product type 2]

**High Infestation:**
- Product types: [specific product type 1], [specific product type 2]

CRITICAL: Mention specific PRODUCT TYPES (not brand names) that we can search on Amazon."""
            else:
                prompt = f"""{context}

Provide treatment recommendations for {self.infestation_level.upper()} infestation.

Recommend 2-3 SPECIFIC product types suitable for {self.plant_type} (e.g., "organic Bt spray for caterpillars", "spinosad concentrate", "neem oil spray").

{"Include manual removal as first option since infestation is low." if self.infestation_level == "low" else ""}

Format in 2 short paragraphs. List specific PRODUCT TYPES (not brand names) that we can search on Amazon."""
            
            try:
                response = self.model.generate_content(prompt)
                treatment_text = response.text.strip()
                
                # Extract product names from recommendations
                # Look for common product keywords
                product_keywords = []
                keywords_to_search = [
                    "Bt", "spinosad", "neem oil", "pyrethrin", "insecticidal soap",
                    "copper fungicide", "sulfur spray", "diatomaceous earth",
                    "horticultural oil", "bacillus thuringiensis"
                ]
                
                treatment_lower = treatment_text.lower()
                for keyword in keywords_to_search:
                    if keyword.lower() in treatment_lower:
                        product_keywords.append(keyword)
                
                # If no specific products found, use general search term
                if not product_keywords:
                    product_keywords = [f"{self.pest_or_disease} treatment {self.plant_type}"]
                
                # Search Amazon for recommended products
                amazon_products = []
                for product_keyword in product_keywords[:2]:  # Limit to 2 searches
                    search_query = f"{product_keyword} organic pesticide"
                    products = search_amazon_products(search_query, max_results=2)
                    amazon_products.extend(products)
                
                # Format Amazon product links
                product_links = "\n\n---\n\n**🛒 Recommended Products on Amazon:**\n\n"
                
                if amazon_products and "error" not in amazon_products[0]:
                    for i, product in enumerate(amazon_products[:4], 1):  # Show top 4
                        if "error" not in product:
                            product_links += f"{i}. **{product['name']}**\n"
                            product_links += f"   💰 {product['price']} | ⭐ {product['rating']}\n"
                            product_links += f"   🔗 [View on Amazon]({product['url']})\n\n"
                else:
                    product_links += "*(Product links temporarily unavailable)*\n"
                
                # Combine treatment recommendations with product links
                answer = treatment_text + product_links
                
                self.conversation_history.append({
                    "type": "menu_selection",
                    "option": option,
                    "answer": answer
                })
                
                return answer
                
            except Exception as e:
                return f"Error generating recommendations: {str(e)}"
                
        elif option == 2:  # Detailed Soil Impact
            soil_props = soil.get('soil_properties', {})
            
            # Show full soil info retrieved from API
            soil_info_display = f"""**Your Soil Type:**
🪨 Name: {soil_props.get('soil_name')}
📊 Texture: {soil_props.get('soil_texture')}
💧 Drainage: {soil_props.get('drainage_class')}
🏖️ Sand: {soil_props.get('sand_percent')}%
🧱 Clay: {soil_props.get('clay_percent')}%
🌾 Silt: {soil_props.get('silt_percent')}%
🧪 pH: {soil_props.get('ph')}
🌿 Organic Matter: {soil_props.get('organic_matter_percent')}%
"""
            
            prompt = f"""First, the user sees their soil information (already displayed above).

Now provide analysis in 3 SHORT paragraphs:

Paragraph 1: Explain what this soil type means for {self.plant_type} cultivation (1 brief paragraph)

Paragraphs 2-3: How this soil affects treatment for {self.pest_or_disease}:
- Application adjustments needed for {soil_props.get('soil_texture')} with {soil_props.get('drainage_class')} drainage
- pH impact on treatment effectiveness

Context:
{context}

Keep it concise - 3 short paragraphs total."""
            
            try:
                response = self.model.generate_content(prompt)
                answer = soil_info_display + "\n\n" + response.text.strip()
            except Exception as e:
                answer = soil_info_display + f"\n\nError generating analysis: {str(e)}"
            
            self.conversation_history.append({
                "type": "menu_selection",
                "option": option,
                "answer": answer
            })
            
            return answer
        
        elif option == 3:  # Weather-Based Timing
            current = weather.get('current', {})
            forecast = weather.get('forecast_3day', [])
            
            # Show 3-day forecast here
            weather_display = f"""**Current Weather:**
🌡️ Temperature: {current.get('temperature')}°{current.get('temperature_unit')}
☁️ Conditions: {current.get('short_forecast')}
💨 Wind: {current.get('wind_speed')} {current.get('wind_direction')}

**3-Day Forecast:**
"""
            for period in forecast[:6]:
                weather_display += f"• {period.get('name')}: {period.get('temperature')}° - {period.get('short_forecast')}\n"
            
            prompt = f"""The user sees their weather information (already displayed above).

Now provide timing guidance in EXACTLY 2 short paragraphs:
- Best application window in next 3 days for treating {self.pest_or_disease}
- Why timing matters (rain, temperature, wind effects)

Context:
{context}

Keep it BRIEF - exactly 2 short paragraphs."""
            
            try:
                response = self.model.generate_content(prompt)
                answer = weather_display + "\n\n" + response.text.strip()
            except Exception as e:
                answer = weather_display + f"\n\nError: {str(e)}"
            
            self.conversation_history.append({
                "type": "menu_selection",
                "option": option,
                "answer": answer
            })
            
            return answer
        
        elif option == 4:  # Monitoring & Prevention
            prompt = f"""{context}

Provide monitoring and prevention advice (EXACTLY 2 short paragraphs):
- How often to check {self.plant_type}
- What signs indicate treatment success/failure
- Prevention tips

Keep it BRIEF - exactly 2 short paragraphs."""
        
        elif option == 5:  # Detailed Report (combines 1-4)
            print("\n⏳ Generating comprehensive detailed report...")
            
            # Generate all sections
            treatment = self.answer_menu_selection(1)
            soil_impact = self.answer_menu_selection(2)
            weather_timing = self.answer_menu_selection(3)
            monitoring = self.answer_menu_selection(4)
            
            detailed_report = f"""
{'=' * 70}
COMPREHENSIVE TREATMENT REPORT
{'=' * 70}

## 1. TREATMENT RECOMMENDATIONS
{treatment}

{'─' * 70}

## 2. SOIL IMPACT ANALYSIS
{soil_impact}

{'─' * 70}

## 3. WEATHER-BASED TIMING
{weather_timing}

{'─' * 70}

## 4. MONITORING & PREVENTION
{monitoring}

{'=' * 70}
"""
            
            self.conversation_history.append({
                "type": "detailed_report",
                "content": detailed_report
            })
            
            return detailed_report
        
        else:
            return "Invalid option. Please select 1-6."
        
        # For options 1 and 4, generate response
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            self.conversation_history.append({
                "type": "menu_selection",
                "option": option,
                "answer": answer
            })
            
            return answer
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ask_custom_question(self, question: str) -> str:
        """
        Handle custom questions using LLM with full context
        EXACTLY 2 paragraphs
        """
        if not self.pest_or_disease:
            return "Please start with image detection first."
        
        weather = self.location_context.get("weather", {}) if self.location_context else {}
        soil = self.location_context.get("soil", {}) if self.location_context else {}
        
        context = f"""
DETECTED ISSUE: {self.pest_or_disease} ({self.severity})
PLANT: {self.plant_type}
INFESTATION LEVEL: {self.infestation_level}
LOCATION: {weather.get('location', {}).get('city') if weather else 'Unknown'}
TEMPERATURE: {weather.get('current', {}).get('temperature') if weather else 'Unknown'}°F
SOIL TEXTURE: {soil.get('soil_properties', {}).get('soil_texture') if soil else 'Unknown'}
SOIL DRAINAGE: {soil.get('soil_properties', {}).get('drainage_class') if soil else 'Unknown'}
"""
        
        prompt = f"""{context}

USER QUESTION: {question}

Provide a helpful answer using the context above. Keep it concise - EXACTLY 2 short paragraphs:"""
        
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            self.conversation_history.append({
                "type": "custom_question",
                "question": question,
                "answer": answer
            })
            
            return answer
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_conversation_history(self):
        return self.conversation_history
    
    def reset_context(self):
        self.pest_or_disease = None
        self.severity = None
        self.subject_type = None
        self.plant_type = None
        self.infestation_level = None
        self.location_context = None
        self.conversation_history = []
