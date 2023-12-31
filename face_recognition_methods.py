import face_recognition
import numpy as np
import os

# Load the known face image(s)
# Encode the known face image(s)
def encode_images(save=True):
    names = np.array([0])
    known_faces_encodings = np.array([np.zeros(128)])
    for i in os.listdir('./images'):
        known_image = face_recognition.load_image_file('./images/' + i)
        face_locations = face_recognition.face_locations(known_image)
        known_face_encoding = face_recognition.face_encodings(known_image, face_locations)[0]

        known_faces_encodings = np.concatenate((known_faces_encodings, [known_face_encoding]))
        names = np.concatenate((names, [i.split('.')[0]]))
    # pop the first element
    known_faces_encodings = np.delete(known_faces_encodings, 0, 0)
    names = np.delete(names, 0, 0)
    # free up memory
    del known_image, face_locations, known_face_encoding
    if save:        
        np.savez("known_faces_data.npz", **{"known_faces_encodings":known_faces_encodings, "names":names})
    return known_faces_encodings, names

def load_faces():
    loaded_data = np.load("known_faces_data.npz")
    known_faces_encodings = loaded_data["known_faces_encodings"]
    names = loaded_data['names']
    return known_faces_encodings, names