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

def set_authorized_encodings(file_path):
    authorized_encodings = []
    for file in os.listdir(file_path):
        image = face_recognition.load_image_file(file_path + file)
        encoding = face_recognition.face_encodings(image)[0]
        authorized_encodings.append(encoding)
    
    return authorized_encodings

def set_authorized_locations(coords):
    authorized_locations = set()
    for coord in coords:
        authorized_locations.add(coord)
    return authorized_locations

def get_current_location():
    # geolocator = Nominatim(user_agent='geolocator_app')
    ip_request = requests.get("https://api64.ipify.org?format=json")
    ip_address = ip_request.json()['ip']

    location_request = requests.get(f"https://ipinfo.io/{ip_address}/json")
    location_data = location_request.json()

    lat, lon = location_data['loc'].split(',')
    return (float(lat), float(lon))

def check_authorized_locations(current_location, authorized_locations):
    print(current_location)
    print(authorized_locations)
    return current_location not in authorized_locations

def resize_frame(frame, scale):
    transform_coords = 1 / scale
    return cv2.resize(frame, (0, 0,), fx=scale, fy=scale), transform_coords

def sleep_mac():
    os.system('osascript -e \'tell application "System Events" to sleep\'')

def run_face_recognition(authorized_locations, authorized_encodings, current_location):
    video_capture = cv2.VideoCapture(0)
    scale = 0.25
    
    while True:
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
        
        # current_location = get_current_location()
        if unauthorized_present or check_authorized_locations(current_location, authorized_locations):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'img_{timestamp}.png'
            # detecting unauthorized entity or unauthorized_location
            cv2.putText(frame, 'Unauthorized Person/Location Detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imwrite(f'unauthorized_logs/{filename}', frame)
            # instead of logging out here add a secondary form of authentication (MFA)

            # sleep_mac()
            # sys.exit(0)
            
        else:
            cv2.putText(frame, 'Authorized Person and Location Detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()

def main():
    authorized_locations = set_authorized_locations([(35.2635, -120.6509)])
    authorized_encodings = set_authorized_encodings("authorized_faces/")
    current_location = get_current_location()
    run_face_recognition(authorized_locations, authorized_encodings, current_location)

if __name__ == '__main__':
    main()

