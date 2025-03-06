from geopy.geocoders import Nominatim
import requests

authorized_locations = set([(35.2635, -120.6509)])


geolocator = Nominatim(user_agent="geolocator_app")

# Get public IP address
ip_request = requests.get("https://api64.ipify.org?format=json")
ip_address = ip_request.json()['ip']

location_request = requests.get(f"https://ipinfo.io/{ip_address}/json")
location_data = location_request.json()

location = geolocator.geocode('1127 Tulip Court, San Luis Obispo, CA 93401')
print(location.latitude, location.longitude)


lat, lon = location_data['loc'].split(',')
lat, lon = float(lat), float(lon)
print(lat, lon)
if (lat, lon) not in authorized_locations:
    print("Unauthorized access detected!")
    print(f"Unauthorized location: {lat}, {lon}")
else:
    print("Authorized access detected!")
    print(f"Authorized location: {lat}, {lon}")

print