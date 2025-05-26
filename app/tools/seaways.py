from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict

def get_seaways_route_info(
    source_port: str,
    destination_port: str,
    cargo_tonnage: float = 10,
    freight_rate_per_tonne_km: float = 0.05
) -> Dict:
    """
    Estimate seaway shipping details including distance, carbon emissions, and freight cost.

    This tool calculates the estimated seaway route information between two global ports using their geolocations.
    It computes:
    - The straight-line distance (in kilometers) between the ports
    - The estimated CO₂ emissions in kilograms based on the cargo tonnage (using a rough factor of 0.02 kg CO₂ per tonne-km)
    - The estimated shipping price in USD based on the tonnage and freight rate per tonne-km

    Args:
        source_port: Name of the source port (e.g. "Mundra Port, India")
        destination_port: Name of the destination port (e.g. "Port of Rotterdam, Netherlands")
        cargo_tonnage: The total cargo weight to be shipped, in metric tonnes (default is 1000 tonnes)
        freight_rate_per_tonne_km: Freight cost rate in USD per tonne-km (default is 0.05 USD)

    Returns:
        A dictionary containing:
            - source_coordinates (lat, lon)
            - destination_coordinates (lat, lon)
            - estimated_distance_km
            - estimated_emission_kg
            - assumed_cargo_tonnage
            - estimated_price_usd
            - freight_rate_per_tonne_km

        Or an error message if geocoding fails.
    """
    print("Executing seasways tool")
    # print({source_port, destination_port, freight_rate_per_tonne_km, cargo_tonnage})

    geolocator = Nominatim(user_agent="seaway_route_calculator")

    try:
        src_location = geolocator.geocode(source_port)
        dst_location = geolocator.geocode(destination_port)

        if not src_location or not dst_location:
            return {"error": "Could not geocode one or both ports."}

        src_coords = (src_location.latitude, src_location.longitude)
        dst_coords = (dst_location.latitude, dst_location.longitude)

        distance_km = geodesic(src_coords, dst_coords).km
        estimated_emission_kg = round(distance_km * cargo_tonnage * 0.02, 2)
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

