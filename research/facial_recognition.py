import cv2
import face_recognition
import numpy as np

authorized_image = face_recognition.load_image_file("arjun_photo.jpg")
authorized_encoding = face_recognition.face_encodings(authorized_image)[0]

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces([authorized_encoding], face_encoding)
        name = 'Unknown'

        if True in matches:
            name = 'Authorized'
            
        top, right, bottom, left = [coord * 4 for coord in face_location]

        color = (0, 255, 0) if name == 'Authorized' else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
        
    cv2.imshow('Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()