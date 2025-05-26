import openrouteservice
from typing import Dict, Any
import asyncio
import os

client = openrouteservice.Client(key=os.getenv("OPEN_ROUTE_SERVICES_API_KEY"))

async def get_road_data(source: str, destination: str) -> Dict[str, Any]:
    """Get comprehensive driving route information between two locations including turn-by-turn directions.
    
    This tool uses OpenRouteService API to find the optimal driving route between any two locations worldwide.
    It provides detailed navigation instructions, distance, estimated travel time, and environmental impact data.
    The tool automatically geocodes location names to coordinates and calculates the best driving route.
    
    Args:
        source: Starting location name or address. Can be a landmark, full address, city name, or point of interest.
                Examples: "India Gate, New Delhi", "123 Main Street, New York", "Paris, France", "Times Square"
        destination: Ending location name or address. Can be a landmark, full address, city name, or point of interest.
                    Examples: "Surat, Gujarat", "Los Angeles International Airport", "Big Ben, London"
    
    Returns:
        A dictionary containing comprehensive route information with the following keys:
        - route_steps: List of strings with turn-by-turn navigation instructions in order
        - total_distance_km: Total driving distance in kilometers (float, rounded to 2 decimal places)
        - estimated_time_min: Estimated driving time in minutes (float, rounded to 2 decimal places)
        - estimated_emission_kg: Estimated CO2 emissions for the trip in kilograms (float, based on average car emissions of 0.192 kg/km)
        
        If an error occurs (invalid locations, network issues, etc.), returns:
        - error: String description of the error that occurred
    
    Note: This tool requires internet connectivity and uses OpenRouteService's geocoding and routing services.
    Travel times are estimates based on typical driving conditions and may vary due to traffic, weather, or road conditions.
    """
    print("Execute roadways tool")

    try:
        # Get coordinates using OpenRouteService geocoding
        src_coords = client.pelias_search(source)["features"][0]["geometry"]["coordinates"]
        dst_coords = client.pelias_search(destination)["features"][0]["geometry"]["coordinates"]

        # Get optimal driving route
        route = client.directions(
            coordinates=[src_coords, dst_coords],
            profile='driving-car',
            format='geojson'
        )

        # Extract route segment data
        segment = route['features'][0]['properties']['segments'][0]
        distance_m = segment['distance']
        duration_s = segment['duration']

        # Extract step-by-step navigation instructions
        steps = segment.get('steps', [])
        instructions = [step['instruction'] for step in steps]

        # Calculate environmental impact
        # Using average car emission factor: 0.192 kg CO2 per kilometer
        distance_km = distance_m / 1000
        emission_kg = round(distance_km * 0.192, 2)

        return {
            "route_steps": instructions,
            "total_distance_km": round(distance_km, 2),
            "estimated_time_min": round(duration_s / 60, 2),
            "estimated_emission_kg": emission_kg
        }

    except IndexError:
        return {"error": "Could not find one or both locations. Please check the spelling and try again with more specific addresses."}
    except openrouteservice.exceptions.ApiError as e:
        return {"error": f"OpenRouteService API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error occurred: {str(e)}"}

def get_roadways_route_info(source: str, destination: str) -> Dict[str, Any]:
    """Get comprehensive driving route information between two locations including turn-by-turn directions.
    
    This tool uses OpenRouteService API to find the optimal driving route between any two locations worldwide.
    It provides detailed navigation instructions, distance, estimated travel time, and environmental impact data.
    The tool automatically geocodes location names to coordinates and calculates the best driving route.
    
    Args:
        source: Starting location name or address. Can be a landmark, full address, city name, or point of interest. Examples: "India Gate, New Delhi", "123 Main Street, New York", "Paris, France", "Times Square"
        destination: Ending location name or address. Can be a landmark, full address, city name, or point of interest. Examples: "Surat, Gujarat", "Los Angeles International Airport", "Big Ben, London"
    
    Returns:
        A dictionary containing comprehensive route information with the following keys:
        - route_steps: List of strings with turn-by-turn navigation instructions in order
        - total_distance_km: Total driving distance in kilometers (float, rounded to 2 decimal places)
        - estimated_time_min: Estimated driving time in minutes (float, rounded to 2 decimal places)
        - estimated_emission_kg: Estimated CO2 emissions for the trip in kilograms (float, based on average car emissions of 0.192 kg/km)
        
        If an error occurs (invalid locations, network issues, etc.), returns:
        - error: String description of the error that occurred
    
    Note: This tool requires internet connectivity and uses OpenRouteService's geocoding and routing services.
    Travel times are estimates based on typical driving conditions and may vary due to traffic, weather, or road conditions.
    """
    asyncio.run(get_road_data(source, destination))