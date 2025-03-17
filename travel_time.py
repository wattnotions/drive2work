import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_travel_time(origin, destination, mode="DRIVE"):
    """
    Fetches the travel time between two locations using Google Routes API.
    
    :param origin: Starting location (e.g., "Dublin, Ireland")
    :param destination: Destination location (e.g., "Cork, Ireland")
    :param mode: Mode of transport ("DRIVE", "BICYCLE", "WALK")
    :return: Travel time as a string
    """
    if not API_KEY:
        return "Error: API key not found. Please check your .env file."

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration"
    }

    data = {
        "origin": {
            "location": {
                "address": origin
            }
        },
        "destination": {
            "location": {
                "address": destination
            }
        },
        "travelMode": mode
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if "routes" in result and result["routes"]:
            travel_time = result["routes"][0]["duration"]
            return f"Estimated travel time from {origin} to {destination} by {mode.lower()}: {travel_time}"
        else:
            return "No route found."
    else:
        return f"Error: {response.status_code}, {response.text}"

if __name__ == "__main__":
    origin = input("Enter the starting location: ")
    destination = input("Enter the destination: ")
    mode = input("Enter mode (DRIVE, WALK, BICYCLE): ").upper() or "DRIVE"

    print(get_travel_time(origin, destination, mode))
