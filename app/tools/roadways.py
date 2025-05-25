import openrouteservice
from typing import Dict, Any

# OpenRouteService client
client = openrouteservice.Client(key="5b3ce3597851110001cf624814f4cd46257b4262a1cefd4eda0ac21f")

def get_route_info(source: str, destination: str) -> Dict[str, Any]:
    try:
        # Get coordinates
        src_coords = client.pelias_search(source)["features"][0]["geometry"]["coordinates"]
        dst_coords = client.pelias_search(destination)["features"][0]["geometry"]["coordinates"]

        # Get route
        route = client.directions(
            coordinates=[src_coords, dst_coords],
            profile='driving-car',
            format='geojson'
        )

        segment = route['features'][0]['properties']['segments'][0]
        distance_m = segment['distance']
        duration_s = segment['duration']

        # Step-by-step instructions
        steps = segment.get('steps', [])
        instructions = [step['instruction'] for step in steps]

        # Calculate carbon emission (car average: 0.192 kg/km)
        distance_km = distance_m / 1000
        emission_kg = round(distance_km * 0.192, 2)

        return {
            "route_steps": instructions,
            "total_distance_km": round(distance_km, 2),
            "estimated_time_min": round(duration_s / 60, 2),
            "estimated_emission_kg": emission_kg
        }

    except Exception as e:
        return {"error": str(e)}

# Test
if __name__ == '__main__':
    result = get_route_info("India Gate, New Delhi", "surat")

    # Output
    if "error" not in result:
        print("Route Steps:")
        for step in result["route_steps"]:
            print("-", step)
        print("Total Distance (km):", result["total_distance_km"])
        print("Estimated Time (min):", result["estimated_time_min"])
        print("Estimated CO₂ Emission (kg):", result["estimated_emission_kg"])
    else:
        print("Error:", result["error"])
