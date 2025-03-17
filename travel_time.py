import os
import requests

# Read API key from api_key.txt
def get_api_key():
    try:
        with open("api_key.txt", "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        print("❌ Error: api_key.txt file not found! Create it and add your API key inside.")
        exit(1)

API_KEY = get_api_key()

def get_lat_lng(address):
    """ Converts an Eircode or address to latitude/longitude using Google Geocoding API. """
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(geocode_url)
    data = response.json()

    if response.status_code == 200 and data.get("results"):
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        print(f"❌ API Error: {response.status_code}, {response.text}")
        exit(1)

def get_travel_time():
    """
    Fetches travel time between D06 EV22 (Starting) and D11 VNW2 (Destination) using Google Routes API.
    """
    origin = "D06EV22"  # Hardcoded Starting Eircode
    destination = "D11VNW2"  # Hardcoded Destination Eircode
    travel_mode = "DRIVE"  # Hardcoded mode

    print(f"📍 Using hardcoded locations: {origin} → {destination} (Mode: {travel_mode})")

    origin_lat, origin_lng = get_lat_lng(origin)
    destination_lat, destination_lng = get_lat_lng(destination)

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration"
    }

    data = {
        "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
        "destination": {"location": {"latLng": {"latitude": destination_lat, "longitude": destination_lng}}},
        "travelMode": travel_mode
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if "routes" in result and result["routes"]:
            # Extract duration and convert from string to integer
            travel_time_str = result["routes"][0]["duration"]  # Example: "1601s"
            travel_time_seconds = int(travel_time_str[:-1])  # Remove last character ('s') and convert to int
            travel_time_minutes = round(travel_time_seconds / 60)  # Convert to minutes

            return f"🚗 Estimated travel time from {origin} to {destination} (DRIVING): {travel_time_minutes} minutes"

        else:
            return "⚠️ No route found."
    else:
        return f"❌ API Error: {response.status_code}, {response.text}"

if __name__ == "__main__":
    print(f"✅ API Key Loaded Successfully: {API_KEY[:5]}*****")  # Show partial key
    print(get_travel_time())
