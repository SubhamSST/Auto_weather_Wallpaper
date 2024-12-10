import os
import ctypes
import requests
import time
import sys
import winreg as reg
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Constants and paths
UNSPLASH_URL = 'https://api.unsplash.com/photos/random'
WALLPAPER_PATH = "wallpaper.jpg"
EXE_PATH = sys.executable 


def add_to_registry():
    key = reg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    key_name = "MyWallpaperApp"

    try:
        with reg.OpenKey(key, key_path, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, key_name, 0, reg.REG_SZ, EXE_PATH)
            print(f"Successfully added to startup: {EXE_PATH}")
    except Exception as e:
        print(f"Failed to add to registry: {e}")


def get_location():
    try:
        response = requests.get("http://ip-api.com/json")
        response.raise_for_status()
        data = response.json()
        city = data.get("city", "unknown")
        print(f"Detected location: {city}")
        return city
    except requests.exceptions.RequestException as e:
        print(f"Error fetching location: {e}")
        return None


def set_wallpaper(wallpaper_path):
    SPI_SETDESKWALLPAPER = 20
    absolute_path = os.path.abspath(wallpaper_path)
    print(f"Setting wallpaper: {absolute_path}")
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, absolute_path, 3)

def get_weather_data(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def select_weather_based_wallpaper(city):
    weather_data = get_weather_data(city)
    if weather_data:
        description = weather_data['weather'][0]['description'].lower()
        print(f"Weather: {description}")
        return description
    return "default"

def fetch_wallpaper_from_unsplash(query):
    headers = {'Authorization': f'Client-ID {UNSPLASH_API_KEY}'}
    params = {'query': query, 'count': 1}
    try:
        response = requests.get(UNSPLASH_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        image_url = data[0]['urls']['full']
        print(f"Wallpaper URL: {image_url}")
        return image_url
    except requests.exceptions.RequestException as e:
        print(f"Error fetching wallpaper: {e}")
        return None

def download_wallpaper(image_url):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(WALLPAPER_PATH, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print("Wallpaper downloaded successfully.")
        return os.path.abspath(WALLPAPER_PATH)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading wallpaper: {e}")
        return None

def change_wallpaper():
    city = get_location() or "Sambalpur"
    query = select_weather_based_wallpaper(city) or "default"
    wallpaper_url = fetch_wallpaper_from_unsplash(query)
    if wallpaper_url:
        wallpaper_path = download_wallpaper(wallpaper_url)
        if wallpaper_path:
            set_wallpaper(wallpaper_path)

if __name__ == "__main__":
    add_to_registry()
    while True:
        change_wallpaper()
        time.sleep(1800)  #30 minutes
