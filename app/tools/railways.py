from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from geopy.distance import geodesic
import time

# Predefined lat/lng for common stations (extend as needed)
station_coords = {
    "new-delhi-ndls": (28.6422, 77.2195),
    "mumbai-central-mmct": (18.9696, 72.8195),
    # Add more stations if needed
}

def get_train_data(source: str, destination: str):
    date = datetime.now().strftime("%d-%m-%Y")
    url = f"https://www.trainman.in/trains/{source}/{destination}?date={date}&class=ALL&quota=GN&fcs_opt=false"

    options = Options()
    options.add_argument('--start-maximized')  # Browser maximized
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    time.sleep(5)  # Wait for page load

    elems = driver.find_elements(By.CLASS_NAME, 'train-item-container')
    print(f"{len(elems)} trains found between {source} and {destination}.")

    result = []
    for elem in elems:
        card_html = elem.get_attribute('outerHTML')
        soup = BeautifulSoup(card_html, 'html.parser')

        content = {}

        train_name = soup.find('span', attrs={'class': 'short-name'})
        content['train_name'] = train_name.get_text(strip=True) if train_name else None

        train_number_div = soup.find('div', attrs={'class': 'train-route'})
        train_number = train_number_div.find(string=True, recursive=False).strip() if train_number_div else None
        content['train_number'] = train_number

        time_tag = soup.find('span', attrs={'class': 'duration-time'})
        content['expected_time'] = time_tag.get_text(strip=True) if time_tag else None

        fares = {}
        classes = soup.find_all('div', attrs={'class': 'class'})
        fares_html = soup.find_all('div', attrs={'class': 'fare'})

        for cls, fare in zip(classes, fares_html):
            fares[cls.get_text(strip=True)] = fare.get_text(strip=True)

        content['price'] = fares

        # Distance and Emissions
        if source in station_coords and destination in station_coords:
            dist = geodesic(station_coords[source], station_coords[destination]).km
            emission = round(dist * 0.041, 2)  # kg CO₂

            content['distance_km'] = round(dist, 2)
            content['estimated_emission_kg'] = emission
        else:
            content['distance_km'] = None
            content['estimated_emission_kg'] = None

        result.append(content)

    driver.quit()
    return result

if __name__ == '__main__':
    trains = get_train_data("new-delhi-ndls", "mumbai-central-mmct")
    for train in trains:
        print(train)
