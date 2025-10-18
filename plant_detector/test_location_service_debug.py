# test_location_service_debug.py

import sys
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from location_service import LocationService


def test_raw_api():
    """
    Test the SoilGrids API directly to see raw response
    """
    print("\n" + "=" * 70)
    print("DEBUG: Raw SoilGrids API Test")
    print("=" * 70)
    
    service = LocationService()
    zipcode = "92336"
    
    # Get coordinates
    coords = service.zip_to_coordinates(zipcode)
    print(f"\nCoordinates: {coords}")
    
    if coords:
        lat, lon = coords
        
        # Call SoilGrids API directly
        soil_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        
        params = {
            'lon': lon,
            'lat': lat,
            'property': ['clay', 'sand', 'silt', 'phh2o', 'soc'],
            'depth': ['0-5cm', '5-15cm'],
            'value': 'mean'
        }
        
        print(f"\nAPI URL: {soil_url}")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        
        print("\nCalling API...")
        try:
            response = requests.get(soil_url, params=params, timeout=15)
            print(f"Status Code: {response.status_code}")
            print(f"\nRaw Response:")
            print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_raw_api()
