#!/usr/bin/env python3
import sys
import json
import random
import datetime
import requests
import os

def speech(text):
    """
    Updates the global `o` dictionary with a speech text entry.

    Args:
        text (str): The text to be assigned as the speech content.

    Returns:
        None
    """
    global o
    o["speech"] = {"text": text}

def get_lat_lon():
    """
    Fetches the latitude and longitude of the current user based on their IP address.

    Returns:
        tuple or None: 
            tuple containing latitude and longitude as floats (latitude, longitude) if successful, 
            or `None` if the geolocation data is unavailable or an error occurs.
    """
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()

        # Extract latitude and longitude
        loc = data.get("loc")  # "latitude,longitude" string
        if loc:
            latitude, longitude = map(float, loc.split(","))
            return latitude, longitude
        else:
            print("Location information not available.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching geolocation: {e}")
        return None

latitude, longitude = get_lat_lon()

# Get JSON from stdin and load into Python dict
o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

# Get the current script directory for dynamic paths
current_dir = os.path.dirname(os.path.abspath(__file__))

if intent == "GetTime":
    now = datetime.datetime.now()
    speech("It's %s:%02d:%02d." % (now.strftime("%H"), now.minute, now.second))

elif intent == "CreateFile":
    try:
        # Dynamic path for creating the file in the same directory as the script
        file_path = os.path.join(current_dir, "Rhasspy-HelloWorld.txt")
        with open(file_path, 'w') as fp:
            fp.write(json.dumps(o))
        speech("File has been created.")
    except Exception as e:
        speech(f"Failed to create file: {str(e)}")

elif intent == "GetTemperature":
    try:
        # Get weather data from Open-Meteo API
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,  # Example: Berlin, Germany
            "longitude": longitude,
            "current_weather": True
        }
        response = requests.get(url, params=params)
        data = response.json()

        # Extract temperature and precipitation
        current_weather = data.get("current_weather", {})
        temperature = current_weather.get("temperature")
        precipitation = current_weather.get("precipitation", 0.0)  # Default to 0.0 if missing

        # Respond with weather information
        speech(f"It's {temperature} degrees Celsius, and the current precipitation is {precipitation} mm.")
    except Exception as e:
        speech(f"Failed to get temperature: {str(e)}")

elif intent == "Hello":
    replies = ['Hi!', 'Hello!', 'Hey there!', 'Greetings.']
    speech(random.choice(replies))

# Output the JSON response for Rhasspy
print(json.dumps(o))
