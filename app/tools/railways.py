from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from geopy.distance import geodesic
import time
import asyncio

def get_train_data(
    source_code: str,
    destination_code: str,
    source_lat: float,
    source_lng: float,
    dest_lat: float,
    dest_lng: float
) -> list:
    """
    Get train schedule and fare info between two stations from Ixigo.
    
    Args:
        source_code: Station code like 'PUNE'
        destination_code: Station code like 'NDLS'
        source_lat, source_lng: Source coordinates
        dest_lat, dest_lng: Destination coordinates
        
    Returns:
        List of train data with name, number, duration, fares, distance, and CO2 emission.
    """
    date = (datetime.now() + timedelta(days=20)).strftime("%d%m%Y")
    url = f"https://www.ixigo.com/search/result/train/{source_code}/{destination_code}/{date}//1/0/0/0/ALL"
    
    options = Options()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless=new')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'train-listing-row'))
        )
    except Exception as e:
        print("❌ Train data not loaded:", e)
        driver.quit()
        return []

    elems = driver.find_elements(By.CLASS_NAME, 'train-listing-row')
    print(f"{len(elems)} trains found.")

    result = []
    for elem in elems:
        card_html = elem.get_attribute('outerHTML')
        soup = BeautifulSoup(card_html, 'html.parser')

        content = {}

        name_tag = soup.find('span', class_='train-name')
        num_tag = soup.find('span', class_='train-number')
        time_tag = soup.find('div', class_='c-timeline-wrapper')

        content['train_name'] = name_tag.get_text(strip=True) if name_tag else None
        content['train_number'] = num_tag.get_text(strip=True) if num_tag else None
        content['expected_time'] = time_tag.get_text(strip=True) if time_tag else None

        fares = {}
        classes = soup.find_all('span', class_='train-class')
        prices = soup.find_all('div', class_='c-price-display')

        for cls, price in zip(classes, prices):
            fares[cls.get_text(strip=True)] = price.get_text(strip=True)

        content['price'] = fares

        # Distance & Emission
        dist_km = round(geodesic((source_lat, source_lng), (dest_lat, dest_lng)).km, 2)
        co2_emission = round(dist_km * 0.041, 2)

        content['distance_km'] = dist_km
        content['estimated_emission_kg'] = co2_emission

        result.append(content)

        if len(result) >= 3:  # limit results for speed
            break

    driver.quit()
    return result

def get_railways_route_info(
    source_code: str,
    destination_code: str,
    source_lat: float,
    source_lng: float,
    dest_lat: float,
    dest_lng: float
) -> list:
    """
    Get train schedule and fare info between two stations from Ixigo.
    
    Args:
        source_code: Station code like 'PUNE'
        destination_code: Station code like 'NDLS'
        source_lat: Source latitude
        source_lng: Source longitude
        dest_lat: Destination Latitude
        dest_lng: Destination longitude

    Returns:
        A list of dictionaries, each containing train information with the following keys:
        - train_name: Name of the train (string)
        - train_number: Official train number (string)
        - expected_time: Journey duration in hours and minutes (string)
        - price: Dictionary with class names as keys and fare prices as values
        - distance_km: Distance between stations in kilometers (float)
        - estimated_emission_kg: Estimated CO2 emissions in kilograms (float)
    """
    asyncio.run(get_train_data(source_code, destination_code, source_lat, source_lng, dest_lat, dest_lng))

if __name__ == '__main__':
    print("test")
    result = get_railways_route_info(
        source_code="PUNE",
        destination_code="NDLS",
        source_lat=18.5286,
        source_lng=73.8743,
        dest_lat=28.6448,
        dest_lng=77.2167
    )
    print(result)