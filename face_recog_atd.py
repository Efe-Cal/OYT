from text2speech import text2speech
import datetime
import cv2
import face_recognition
import numpy as np
from time import time, sleep
import socket
from face_recognition_methods import *


# known_faces_encodings, names = encode_images()
# or
known_faces_encodings, names = load_faces()

# Initialize the video capture
video_capture = cv2.VideoCapture(0)

faces_found=[]
text_shown=0,""
while True:
    ret, image = video_capture.read()
    # Convert the frame to RGB format
    rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect faces in the frame
    cam_face_locations = face_recognition.face_locations(rgb_frame)
    cam_face_encodings = face_recognition.face_encodings(rgb_frame, cam_face_locations)

    # Compare the detected face(s) with the known face(s)
    for face_encoding, face_location in zip(cam_face_encodings, cam_face_locations):
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        name = ""

        if True in matches:
            name = names[matches.index(True)]
            faces_found.append([name,datetime.datetime.now().strftime("%H.%M")])
            known_faces_encodings = np.delete(known_faces_encodings, matches.index(True), 0)
            names = np.delete(names, matches.index(True), 0)
            print(name, "bulundu")
            text_shown=time(),name

        # Draw rectangle around the detected face
        top, right, bottom, left = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if time()-text_shown[0]<2:
        cv2.putText(image, text_shown[1] + " yoklamaya kaydedildi", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    else:text_shown=0,""
    cv2.imshow('Face Recognition', image)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key==27:
        break

# Release the video capture
video_capture.release()
cv2.destroyAllWindows()

faces_found_names = [row[0] for row in faces_found]

missing_names = [name for name in names if name not in faces_found_names]
print("Yoklamaya katılmayanlar:", missing_names)
text2speech("Yoklamaya katılmayanlar " + " ".join(missing_names))
if input()!="":
    hostname = socket.gethostname()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 5555))
        s.sendall(bytes("\n".join(list(map(lambda x:":".join(x),faces_found))), 'utf-8'))
        s.close()