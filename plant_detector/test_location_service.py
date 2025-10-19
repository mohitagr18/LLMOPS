# test_location_service.py

import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from location_service import LocationService


def test_location_service():
    """
    Test location service - weather + USDA soil data
    """
    print("\n" + "=" * 70)
    print("STEP 2.1 TEST: Weather + USDA Soil Data")
    print("=" * 70)
    
    service = LocationService()
    
    test_zips = ["92336", "10001"]
    
    for zipcode in test_zips:
        print(f"\n{'─' * 70}")
        print(f"Testing ZIP Code: {zipcode}")
        print("─" * 70)
        
        # Test weather
        print(f"\n📡 Fetching weather data...")
        weather = service.get_weather_data(zipcode)
        
        if "error" not in weather:
            print(f"✓ Weather retrieved")
            print(f"  📍 {weather['location']['city']}, {weather['location']['state']}")
            print(f"  🌡️  {weather['current']['temperature']}°{weather['current']['temperature_unit']}")
            print(f"  💨 {weather['current']['wind_speed']} {weather['current']['wind_direction']}")
            print(f"  ☁️  {weather['current']['short_forecast']}")
            
            # Display 3-day forecast
            print(f"\n  📅 3-Day Forecast:")
            for period in weather['forecast_3day']:
                temp = period.get('temperature')
                name = period.get('name')
                forecast = period.get('short_forecast')
                print(f"    • {name}: {temp}° - {forecast}")
        else:
            print(f"✗ {weather['error']}")
        
        # Test soil
        print(f"\n🌱 Fetching USDA soil data...")
        soil = service.get_soil_data(zipcode)
        
        if "error" not in soil:
            props = soil.get('soil_properties', {})
            
            print(f"✓ Soil data retrieved")
            print(f"  🏷️  Soil Name: {props.get('soil_name', 'Unknown')}")
            print(f"  📋 Component: {props.get('component_name', 'Unknown')}")
            print(f"  🗂️  Soil Order: {props.get('soil_order', 'Unknown')}")
            print(f"  💧 Drainage: {props.get('drainage_class', 'Unknown')}")
            print(f"  🪨 Texture: {props.get('soil_texture', 'Unknown')}")
            
            # Only show percentages if available
            sand = props.get('sand_percent')
            clay = props.get('clay_percent')
            silt = props.get('silt_percent')
            ph = props.get('ph')
            om = props.get('organic_matter_percent')
            
            if sand != "Not available":
                print(f"  📊 Sand: {sand}%")
            if clay != "Not available":
                print(f"  📊 Clay: {clay}%")
            if silt != "Not available":
                print(f"  📊 Silt: {silt}%")
            if ph != "Not available":
                print(f"  🧪 pH: {ph}")
            if om != "Not available":
                print(f"  🌿 Organic Matter: {om}%")
            
            print(f"  📚 Source: {soil.get('data_source', 'Unknown')}")
            
            if 'note' in soil:
                print(f"  ℹ️  Note: {soil['note']}")
        else:
            print(f"✗ {soil['error']}")
    
    print("\n" + "=" * 70)
    print("STEP 2.1 TEST COMPLETE ✓")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_location_service()
