#!/usr/bin/env python3
import readline
import sys
import json
import random
import datetime
import requests
import os
import pandas as pd

def speech(text):
    global o
    o["speech"] = {"text": text}

def get_lat_lon_general():  
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
    
def get_lat_lon_city(city):
    # Read the CSV file into a DataFrame
    df = pd.read_csv('nl.csv')
    # Define the search city (value in the first column)
    search_city = city
    # Search for the city in the first column
    found_city = df[df.iloc[:, 0] == search_city]

    # Get values from the second and third columns
    if not found_city.empty:
        latitude = found_city.iloc[0, 1]  # Value from the second column
        longitude = found_city.iloc[0, 2]
        return latitude, longitude

cities_set = {}

with open('config/cities', 'r') as file:
    for line in file:
        cities_set.add(line.lower())

for word in text:
    if word in cities_set:
        latitude, longitude = get_lat_lon_city(word)
    else:
        latitude, longitude = get_lat_lon_general()

# Get JSON from stdin and load into Python dict
o = json.loads(sys.stdin.read())

intent = o["intent"]["name"]

# Get the current script directory for dynamic paths
current_dir = os.path.dirname(os.path.abspath(__file__))

# match intent with action
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
