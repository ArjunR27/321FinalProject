import cv2
import face_recognition
import numpy as np
import os
from geopy.geocoders import Nominatim
import requests
import time
import threading
import sys
import datetime
from google_authenticator import verify
import os
from dotenv import load_dotenv

load_dotenv()

# Sets which faces are authorized using the 'authorized_faces' directory
def set_authorized_encodings(file_path):
    authorized_encodings = []
    for file in os.listdir(file_path):
        image = face_recognition.load_image_file(os.path.join(file_path, file))
        encoding = face_recognition.face_encodings(image)
        # Grab only the first encoding
        if encoding:
            authorized_encodings.append(encoding[0])
    
    print(len(authorized_encodings))
    return authorized_encodings

# Sets authorized locations (manually fed for now)
def set_authorized_locations(coords):
    authorized_locations = set()
    for coord in coords:
        authorized_locations.add(coord)
    return authorized_locations

# Gets the current location of the user through ip request and location request
def get_current_location():
    # geolocator = Nominatim(user_agent='geolocator_app')
    ip_request = requests.get("https://api64.ipify.org?format=json")
    ip_address = ip_request.json()['ip']

    location_request = requests.get(f"https://ipinfo.io/{ip_address}/json")
    location_data = location_request.json()

    lat, lon = location_data['loc'].split(',')
    return (float(lat), float(lon))

# Updates location every 3 minutes when program is running in a seperate thread
def update_location_periodically(location, stop_event):
    while not stop_event.is_set():
        new_location = get_current_location()
        print('getting new location')
        if new_location:
            location[0] = new_location
        time.sleep(10)

# Checks if the user is in an authorized location
def check_in_authorized_locations(current_location, authorized_locations):
    print(current_location)
    print(authorized_locations)
    return current_location not in authorized_locations

# Resizes the facial capture frame
def resize_frame(frame, scale):
    transform_coords = 1 / scale
    return cv2.resize(frame, (0, 0,), fx=scale, fy=scale), transform_coords

# Puts the mac to sleep
def sleep_mac():
    os.system('osascript -e \'tell application "System Events" to sleep\'')

# Runs face recognition
# Saves any unauthorized facial captures to 'unauthorized-logs' 
def run_face_recognition(authorized_locations, authorized_encodings, location):
    video_capture = cv2.VideoCapture(0)
    scale = 0.50
    
    while True:
        verified = False
        ret, frame = video_capture.read()

        small_frame, transform_coords = resize_frame(frame, scale)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        unauthorized_present = False
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(authorized_encodings, face_encoding)
            name = 'Unknown'
            print(matches)
            if True in matches:
                name = 'Authorized'
            else:
                unauthorized_present = True

            top, right, bottom, left = [int(coord * transform_coords) for coord in face_location]

            color = (0, 255, 0) if name == 'Authorized' else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
        
        current_location = location[0]
        if unauthorized_present or check_in_authorized_locations(current_location, authorized_locations):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'img_{timestamp}.png'

            cv2.putText(frame, 'Unauthorized Person/Location Detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite(f'unauthorized_logs/{filename}', frame)

            secret = os.getenv('AUTHENTICATOR_SECRET')
            if verify(secret) and not verified:
                print(f"Google Authenticator Verified User")
                verified = True
            else:
                sleep_mac()
                video_capture.release()
                cv2.destroyAllWindows()
                sys.exit(0)

        elif not unauthorized_present and check_in_authorized_locations(current_location, authorized_locations):
            cv2.putText(frame, 'Authorized Person in Unauthorized Location', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
        else:
            cv2.putText(frame, 'Authorized Person and Location Detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()

# Main loop
def main():
    # Home (35.2635, -120.6509)
    # The Avenue (35.2635, -120.6509)
    authorized_locations = set_authorized_locations([(35.2635, -120.6509), (35.2828, -120.6596)])
    authorized_encodings = set_authorized_encodings("authorized_faces/")
    current_location = get_current_location()
    location = [current_location]
    stop_event = threading.Event()

    # Separate thread to keep track of device location
    location_thread = threading.Thread(target=update_location_periodically, args=(location, stop_event))
    location_thread.daemon = True
    location_thread.start()
    
    try:
        run_face_recognition(authorized_locations, authorized_encodings, location)
    finally:
        stop_event.set()
        location_thread.join()

if __name__ == '__main__':
    main()

