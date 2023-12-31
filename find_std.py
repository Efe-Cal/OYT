import cv2
import face_recognition
from face_recognition_methods import *
import numpy as np
# find index of an elemnt in np array

requseted_name = "Elon"

known_faces_encodings, names = load_faces()

req_face_encoding = known_faces_encodings[np.where(names == requseted_name)[0][0]]

video_paths = ["./vid2.mp4"]
interval = 1000  # 3 seconds in milliseconds
for video_path in video_paths:
    cap = cv2.VideoCapture(video_path)
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    for i in range(0, frame_count, int(fps * (interval / 1000))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, image = cap.read()
        
        # image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        cam_face_locations = face_recognition.face_locations(image)
        cam_face_encodings = face_recognition.face_encodings(image, cam_face_locations)
        
        for face_encoding, face_location in zip(cam_face_encodings, cam_face_locations):
            matches = face_recognition.compare_faces([req_face_encoding], face_encoding)
            
            second = i / fps
            if True in matches:
                print("Bulundu @ {:.1f}".format(second))

    cap.release()
