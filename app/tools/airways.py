from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from geopy.distance import geodesic

# Static airport code to coordinates (for demo)
AIRPORT_COORDS = {
    'DEL': (28.5562, 77.1000),  # Delhi
    'KNU': (26.4042, 80.4101),  # Kanpur
    'BOM': (19.0896, 72.8656),  # Mumbai
    'BLR': (13.1986, 77.7066),  # Bengaluru
    'MAA': (12.9941, 80.1709),  # Chennai
    # Add more as needed
}

def estimate_emission_kgs(distance_km: float) -> float:
    """
    Estimate CO₂ emissions using average value: 90g CO₂/passenger-km for flights.
    """
    return round(distance_km * 0.09, 2)

def estimate_distance_km(src: str, dst: str) -> float:
    src_coords = AIRPORT_COORDS.get(src.upper())
    dst_coords = AIRPORT_COORDS.get(dst.upper())
    if not src_coords or not dst_coords:
        return 0.0
    return round(geodesic(src_coords, dst_coords).km, 2)

def scrape_flight_data(source: str, destination: str, date: str = None):
    if not date:
        date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    url = f"https://www.in.cheapflights.com/flight-search/{source.upper()}-{destination.upper()}/{date}?sort=bestflight_a"
    print(url)

    options = Options()
    options.add_argument("--start-maximized")  # Maximize browser
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(8)  # Wait for content to load

    elems = driver.find_elements(By.CLASS_NAME, 'Fxw9-result-item-container')
    print(f"{len(elems)} flight items found")

    results = []
    distance = estimate_distance_km(source, destination)
    emission = estimate_emission_kgs(distance)

    for elem in elems:
        card_html = elem.get_attribute('outerHTML')
        soup = BeautifulSoup(card_html, 'html.parser')

        content = {}

        # Duration
        duration = soup.find_all('div', attrs={'class': 'vmXl-mod-variant-default'})
        if len(duration) < 2:
            continue
        content['Expected Time'] = duration[1].get_text()

        # Price
        price = soup.find('span', attrs={'class': 'c_f8N-price-text'}) or \
                soup.find('div', attrs={'class': 'e2GB-price-text'})
        if price:
            content['price'] = price.get_text()
        else:
            content['price'] = "N/A"

        # Stops
        stops = soup.find_all('div', attrs={'class': 'c_cgF-mod-variant-full-airport'})
        content['stops'] = stops[1].get_text() if len(stops) == 3 else "None"

        # Distance & Emission
        content['distance_km'] = distance
        content['carbon_emission_kg'] = emission

        results.append(content)

    driver.quit()
    return results

if __name__ == '__main__':
    flights = scrape_flight_data("DEL", "BOM")
    for flight in flights:
        print(flight)
