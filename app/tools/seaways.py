from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict

def get_seaway_route_info(
    source_port: str,
    destination_port: str,
    cargo_tonnage: float = 1000,
    freight_rate_per_tonne_km: float = 0.05  # in USD
) -> Dict:
    geolocator = Nominatim(user_agent="seaway_route_calculator")

    try:
        src_location = geolocator.geocode(source_port)
        dst_location = geolocator.geocode(destination_port)

        if not src_location or not dst_location:
            return {"error": "Could not geocode one or both ports."}

        src_coords = (src_location.latitude, src_location.longitude)
        dst_coords = (dst_location.latitude, dst_location.longitude)

        # Approximate seaway distance (straight-line)
        distance_km = geodesic(src_coords, dst_coords).km

        # Estimate emissions (kg CO₂)
        estimated_emission_kg = round(distance_km * cargo_tonnage * 0.02, 2)

        # Estimate shipping price
        estimated_price_usd = round(distance_km * cargo_tonnage * freight_rate_per_tonne_km, 2)

        return {
            "source_coordinates": src_coords,
            "destination_coordinates": dst_coords,
            "estimated_distance_km": round(distance_km, 2),
            "estimated_emission_kg": estimated_emission_kg,
            "assumed_cargo_tonnage": cargo_tonnage,
            "estimated_price_usd": estimated_price_usd,
            "freight_rate_per_tonne_km": freight_rate_per_tonne_km
        }

    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    result = get_seaway_route_info("Mundra Port, India", "Port of Rotterdam, Netherlands", cargo_tonnage=2000)

    if "error" not in result:
        print("Distance (km):", result["estimated_distance_km"])
        print("CO₂ Emission (kg):", result["estimated_emission_kg"])
        print("Estimated Shipping Price (USD):", result["estimated_price_usd"])
    else:
        print("Error:", result["error"])
