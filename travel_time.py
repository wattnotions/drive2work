import os
import requests
import csv
from datetime import datetime, timedelta

# Read API key from api_key.txt
def get_api_key():
    try:
        with open("/home/bitnami/drive2work/api_key.txt", "r") as file:
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
        return None, None

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

    if origin_lat is None or destination_lat is None:
        return None  # Skip logging if geocoding fails

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration"
    }

    departure_time = (datetime.utcnow() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "origin": {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}},
        "destination": {"location": {"latLng": {"latitude": destination_lat, "longitude": destination_lng}}},
        "travelMode": travel_mode,
        "routingPreference": "TRAFFIC_AWARE",
        "departureTime": departure_time  # Ensure the timestamp is in the future
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        if "routes" in result and result["routes"]:
            travel_time_str = result["routes"][0]["duration"]  # Example: "1601s"
            travel_time_seconds = int(travel_time_str[:-1])  # Remove last character ('s') and convert to int
            travel_time_minutes = round(travel_time_seconds / 60)  # Convert to minutes
            return travel_time_minutes
        else:
            return None
    else:
        print(f"❌ API Error: {response.status_code}, {response.text}")
        return None

def log_travel_time():
    """ Logs the current timestamp and travel time to travel_log.csv """
    travel_time = get_travel_time()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Readable and parseable timestamp

    log_file = "/home/bitnami/drive2work/travel_log.csv"
    file_exists = os.path.isfile(log_file)

    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Travel Time (minutes)"])  # Write header if file is new
        writer.writerow([timestamp, travel_time if travel_time is not None else "ERROR"])

    print(f"✅ Logged: {timestamp}, {travel_time if travel_time is not None else 'ERROR'}")

if __name__ == "__main__":
    print(f"✅ API Key Loaded Successfully: {API_KEY[:5]}*****")  # Show partial key
    log_travel_time()
