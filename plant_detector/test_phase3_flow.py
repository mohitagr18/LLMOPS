# test_phase3_flow.py

import sys
import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from plant_pest_detector import PlantPestDetector
from location_service import LocationService
from qa_engine import AgriQAEngine


def test_phase3_flow(image_path):
    """
    Test Phase 3 with all feedback implemented
    """
    print("\n" + "=" * 70)
    print("PHASE 3 TEST: Enhanced Conversational Flow")
    print("=" * 70)
    
    detector = PlantPestDetector()
    location_service = LocationService()
    qa_engine = AgriQAEngine()
    
    # STEP 1: Quick detection
    print(f"\n📸 Step 1: Analyzing image...")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found")
        return
    
    image = Image.open(image_path)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    image_bytes = buffer.getvalue()
    
    pest, severity, plant, confidence, subject_type = detector.identify(image_bytes)
    
    print(f"\n✓ Detection Complete")
    print(f"  🐛 {pest}")
    print(f"  ⚠️  Severity: {severity}")
    print(f"  🌱 Plant: {plant} (confidence: {confidence})")
    
    # STEP 2: SINGLE combined input prompt
    print("\n" + "=" * 70)
    print("📝 For detailed recommendations, please provide:")
    print("=" * 70)
    print("1. Plant/crop type (if not already detected)")
    print("2. Your zip code")
    print("3. Infestation level: low, medium, or high")
    print("\nExample: 'Tomato, 92336, medium'")
    
    user_input = input("\nYour answer: ").strip()
    
    # Parse input
    parsed = qa_engine.parse_user_input(user_input)
    
    # Use detected plant if user didn't provide one
    plant_type = parsed['plant_type'] if parsed['plant_type'] else plant
    zipcode = parsed['zipcode'] if parsed['zipcode'] else "92336"
    infestation = parsed['infestation_level'] if parsed['infestation_level'] else "Unknown"
    
    print(f"\n⏳ Getting weather and soil data for {zipcode}...")
    weather = location_service.get_weather_data(zipcode)
    soil = location_service.get_soil_data(zipcode)
    
    # STEP 3: Set context and show summary
    qa_engine.set_detection_context(pest, severity, subject_type, plant_type, infestation)
    qa_engine.set_location_context(weather, soil)
    
    summary = qa_engine.generate_initial_summary()
    
    print("\n" + "=" * 70)
    print("📍 LOCATION CONTEXT")
    print("=" * 70)
    print(summary['weather_summary'])
    print("\n" + summary['soil_summary'])
    
    print("\n" + "=" * 70)
    print("⚠️  IMMEDIATE ASSESSMENT")
    print("=" * 70)
    print(summary['immediate_assessment'])
    
    # STEP 4: Interactive menu loop (shows menu after each response)
    while True:
        print("\n" + "=" * 70)
        print("💬 WHAT WOULD YOU LIKE TO KNOW?")
        print("=" * 70)
        for option in qa_engine.get_menu_options():
            print(option)
        
        print("\n" + "─" * 70)
        user_choice = input("Select option (1-6) or 'q' to quit: ").strip()
        
        if user_choice.lower() == 'q':
            break
        
        if user_choice == '6':
            question = input("\n💬 Ask your question: ")
            answer = qa_engine.ask_custom_question(question)
        else:
            try:
                option_num = int(user_choice)
                if option_num < 1 or option_num > 6:
                    print("Invalid option. Please select 1-6.")
                    continue
                answer = qa_engine.answer_menu_selection(option_num)
            except:
                print("Invalid input. Try again.")
                continue
        
        print("\n" + "=" * 70)
        print(answer)
        print("=" * 70)
    
    print("\n✓ Phase 3 test complete!")


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "test_images/plant_leaf.jpg"
    test_phase3_flow(image_path)
