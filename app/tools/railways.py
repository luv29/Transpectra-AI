from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from geopy.distance import geodesic
import time
import asyncio

async def get_train_data(
    source: str, 
    destination: str, 
    source_lat: float, 
    source_lng: float, 
    dest_lat: float, 
    dest_lng: float
) -> list:
    """Get comprehensive train schedule and fare information between two railway stations in India.
    
    This tool scrapes live train data from trainman.in to provide detailed information about available trains
    including schedules, fares across different classes, estimated travel time, distance, and carbon emissions.
    
    Args:
        source: Source railway station code (e.g., "new-delhi-ndls", "mumbai-central-mmct"). 
                Use the URL-friendly station code format with hyphens and lowercase letters.
        destination: Destination railway station code (e.g., "new-delhi-ndls", "mumbai-central-mmct").
                    Use the URL-friendly station code format with hyphens and lowercase letters.
        source_lat: Latitude coordinate of the source railway station (decimal degrees, e.g., 28.6422)
        source_lng: Longitude coordinate of the source railway station (decimal degrees, e.g., 77.2195)
        dest_lat: Latitude coordinate of the destination railway station (decimal degrees, e.g., 18.9696)
        dest_lng: Longitude coordinate of the destination railway station (decimal degrees, e.g., 72.8195)
    
    Returns:
        A list of dictionaries, each containing train information with the following keys:
        - train_name: Name of the train (string)
        - train_number: Official train number (string)
        - expected_time: Journey duration in hours and minutes (string)
        - price: Dictionary with class names as keys and fare prices as values
        - distance_km: Distance between stations in kilometers (float)
        - estimated_emission_kg: Estimated CO2 emissions in kilograms (float)
    """

    print("Executing railways tool") 
    # print({source, destination, source_lat, source_lng, dest_lat, dest_lng})
    
    date = (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y")
    url = f"https://www.trainman.in/trains/{source}/{destination}?date={date}&class=ALL&quota=GN&fcs_opt=false"
    print(url)

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
        source_coords = (source_lat, source_lng)
        dest_coords = (dest_lat, dest_lng)
        
        dist = geodesic(source_coords, dest_coords).km
        emission = round(dist * 0.041, 2)  # kg CO₂ per km for train travel

        content['distance_km'] = round(dist, 2)
        content['estimated_emission_kg'] = emission

        result.append(content)

    driver.quit()
    return result

def get_railways_route_info(
        source: str, 
    destination: str, 
    source_lat: float, 
    source_lng: float, 
    dest_lat: float, 
    dest_lng: float
) -> list:
    """Get comprehensive train schedule and fare information between two railway stations in India.
    
    This tool scrapes live train data from trainman.in to provide detailed information about available trains
    including schedules, fares across different classes, estimated travel time, distance, and carbon emissions.
    
    Args:
        source: Source railway station code (e.g., "new-delhi-ndls", "mumbai-central-mmct"). 
                Use the URL-friendly station code format with hyphens and lowercase letters.
        destination: Destination railway station code (e.g., "new-delhi-ndls", "mumbai-central-mmct").
                    Use the URL-friendly station code format with hyphens and lowercase letters.
        source_lat: Latitude coordinate of the source railway station (decimal degrees, e.g., 28.6422)
        source_lng: Longitude coordinate of the source railway station (decimal degrees, e.g., 77.2195)
        dest_lat: Latitude coordinate of the destination railway station (decimal degrees, e.g., 18.9696)
        dest_lng: Longitude coordinate of the destination railway station (decimal degrees, e.g., 72.8195)
    
    Returns:
        A list of dictionaries, each containing train information with the following keys:
        - train_name: Name of the train (string)
        - train_number: Official train number (string)
        - expected_time: Journey duration in hours and minutes (string)
        - price: Dictionary with class names as keys and fare prices as values
        - distance_km: Distance between stations in kilometers (float)
        - estimated_emission_kg: Estimated CO2 emissions in kilograms (float)
    """
    asyncio.run(get_train_data(source, destination, source_lat, source_lng, dest_lat, dest_lng))