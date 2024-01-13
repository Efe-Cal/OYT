import face_recognition
import numpy as np
import sqlite3
import io
import os
import sys

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
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
    conn = sqlite3.connect(os.path.join(application_path,"database.db"), detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    if sinif == "all":
        cursor.execute("SELECT face_encode, adSoyad FROM ogrenciler")
    else:
        cursor.execute("SELECT face_encode, adSoyad FROM ogrenciler WHERE sinif = ?", (sinif, ))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    # unzip the data and return
    return [[i for i, j in data],
            [j for i, j in data]]
