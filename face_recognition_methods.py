import face_recognition
import numpy as np
import sqlite3
import io

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
sqlite3.register_converter("array", convert_array)

def encode_image(image_path):
    known_image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(known_image)
    known_face_encoding = face_recognition.face_encodings(known_image, face_locations)[0]
    return known_face_encoding

def load_faces(sinif):
    conn = sqlite3.connect("database.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("SELECT face_encode, adSoyad FROM ogrenciler WHERE sinif = ?", (sinif, ))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    # unzip the data and return
    return [[i for i, j in data],
            [j for i, j in data]]
if __name__ =="__main__":
    print(load_faces("10a"))
# Load the known face image(s)
# # Encode the known face image(s)
# def encode_images(save=True):
#     names = np.array([0])
#     known_faces_encodings = np.array([np.zeros(128)])
#     for i in os.listdir('./images'):
#         known_image = face_recognition.load_image_file('./images/' + i)
#         face_locations = face_recognition.face_locations(known_image)
#         known_face_encoding = face_recognition.face_encodings(known_image, face_locations)[0]

#         known_faces_encodings = np.concatenate((known_faces_encodings, [known_face_encoding]))
#         names = np.concatenate((names, [i.split('.')[0]]))
#     # pop the first element
#     known_faces_encodings = np.delete(known_faces_encodings, 0, 0)
#     names = np.delete(names, 0, 0)
#     # free up memory
#     del known_image, face_locations, known_face_encoding
#     if save:        
#         np.savez("known_faces_data.npz", **{"known_faces_encodings":known_faces_encodings, "names":names})
#     return known_faces_encodings, names

# def load_faces():
#     loaded_data = np.load("known_faces_data.npz")
#     known_faces_encodings = loaded_data["known_faces_encodings"]
#     names = loaded_data['names']
#     return known_faces_encodings, names