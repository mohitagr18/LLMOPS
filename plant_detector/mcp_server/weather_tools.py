# mcp_server/weather_tools.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.fastmcp import FastMCP
from src.location_service import LocationService

# Initialize FastMCP server
mcp = FastMCP("Agricultural Data Tools")

# Initialize location service
location_service = LocationService()


@mcp.tool()
def get_weather(zipcode: str) -> dict:
    """
    Get current weather conditions and 3-day forecast for a US zip code.
    Returns RAW weather data for the model to use as context.
    
    Args:
        zipcode: 5-digit US zip code
        
    Returns:
        Weather data including temperature, wind, conditions, and forecast
    """
    return location_service.get_weather_data(zipcode)


@mcp.tool()
def get_soil_type(zipcode: str) -> dict:
    """
    Get soil type and properties for a US zip code.
    Returns RAW soil data for the model to use as context.
    
    Args:
        zipcode: 5-digit US zip code
        
    Returns:
        Soil data including soil type, texture, drainage, pH
    """
    return location_service.get_soil_data(zipcode)


@mcp.tool()
def get_location_context(zipcode: str) -> dict:
    """
    Get comprehensive location context including weather AND soil data.
    Returns ALL raw data for the model to generate contextual advice.
    
    Args:
        zipcode: 5-digit US zip code
        
    Returns:
        Combined weather and soil data for agricultural decision-making
    """
    weather = location_service.get_weather_data(zipcode)
    soil = location_service.get_soil_data(zipcode)
    
    return {
        "zipcode": zipcode,
        "weather": weather,
        "soil": soil
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
