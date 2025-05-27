from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from geopy.distance import geodesic
from typing import List, Dict
import time

def estimate_emission_kgs(distance_km: float) -> float:
    """
    Estimate CO₂ emissions using the average value of 90g CO₂ per passenger-km for flights.
    """
    return round(distance_km * 0.09, 2)

def estimate_distance_km(src_coords: tuple, dst_coords: tuple) -> float:
    return round(geodesic(src_coords, dst_coords).km, 2)

def get_airways_route_info(
    source_code: str,
    destination_code: str,
    source_lat: float,
    source_lng: float,
    dest_lat: float,
    dest_lng: float
) -> List[Dict]:
    """
    Scrape flight route information between two airports and estimate carbon emissions.

    This tool scrapes flight options from CheapFlights between two airports on a given date. It also computes:
    - Straight-line distance in kilometers
    - Estimated CO₂ emissions in kilograms based on 90g/passenger-km

    Args:
        source_code: IATA airport code of source (e.g., 'DEL' for Delhi)
        destination_code: IATA airport code of destination (e.g., 'BOM' for Mumbai)
        source_lat: Latitude of the source airport
        source_lng: Longitude of the source airport
        dest_lat: Latitude of the destination airport
        dest_lng: Longitude of the destination airport

    Returns:
        A list of flights with details including duration, price, stops, distance, and CO₂ emissions.
    """
    
    print("Executing airways tool") 
    # print({source_code, destination_code, source_lat, source_lng, dest_lat, dest_lnge})

    date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    url = f"https://www.in.cheapflights.com/flight-search/{source_code.upper()}-{destination_code.upper()}/{date}?sort=bestflight_a"
    print(url)

    options = Options()
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(15)  # Wait for content to load

    elems = driver.find_elements(By.CLASS_NAME, 'Fxw9-result-item-container')
    print(f"{len(elems)} flight items found")

    results = []
    distance = estimate_distance_km((source_lat, source_lng), (dest_lat, dest_lng))
    emission = estimate_emission_kgs(distance)

    for elem in elems:
        card_html = elem.get_attribute('outerHTML')
        soup = BeautifulSoup(card_html, 'html.parser')

        content = {}

        # Duration
        duration = soup.find_all('div', attrs={'class': 'vmXl-mod-variant-default'})
        if len(duration) < 2:
            continue
        content['expected_time'] = duration[1].get_text()

        # Price
        price = soup.find('span', attrs={'class': 'c_f8N-price-text'}) or \
                soup.find('div', attrs={'class': 'e2GB-price-text'})
        content['price'] = price.get_text() if price else "N/A"

        # Stops
        stops = soup.find_all('div', attrs={'class': 'c_cgF-mod-variant-full-airport'})
        content['stops'] = stops[1].get_text() if len(stops) == 3 else "None"

        # Distance & Emission
        content['distance_km'] = distance
        content['carbon_emission_kg'] = emission

        results.append(content)

    driver.quit()
    return results
