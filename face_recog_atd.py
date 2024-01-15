import os
import sys
from text2speech import text2speech
import datetime
import cv2
import face_recognition
import numpy as np
from time import time
from face_recognition_methods import *
from requsetData import getFaceEncodings, getDersProg
import requests
import json
import tkinter as tk

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
def getConfig():
    # tkinter window for config data
    window = tk.Tk()
    window.title("Yoklama")
    window.geometry("270x165")
    # start at the center of the screen
    window.eval('tk::PlaceWindow . center')
    window.resizable(False, False)
    # tkinter variables
    host = tk.StringVar()
    port = tk.StringVar()
    okul = tk.StringVar()
    sinif = tk.StringVar()
    saat = tk.StringVar()
    password = tk.StringVar()
    # tkinter widgets
    tk.Label(window, text="Sınıf:").grid(row=0, column=0, sticky="W")
    tk.Entry(window, textvariable=sinif).grid(row=0, column=1)
    tk.Label(window, text="Yoklama gönderim saati:").grid(row=1, column=0, sticky="W")
    tk.Entry(window, textvariable=saat).grid(row=1, column=1)
    tk.Label(window, text="Host:").grid(row=2, column=0, sticky="W")
    tk.Entry(window, textvariable=host).grid(row=2, column=1)
    tk.Label(window, text="Port:").grid(row=3, column=0, sticky="W")    
    tk.Entry(window, textvariable=port).grid(row=3, column=1)
    tk.Label(window, text="Okul:").grid(row=4, column=0, sticky="W")    
    tk.Entry(window, textvariable=okul).grid(row=4, column=1)
    tk.Label(window, text="Sunucu Şifresi:").grid(row=5, column=0, sticky="W")
    tk.Entry(window, textvariable=password).grid(row=5, column=1)
    tk.Button(window, text="Kaydet", command=window.destroy).grid(row=6, column=1)
    window.mainloop()
    return {"sinif":sinif.get().lower(),"host":host.get(), "port":port.get(), "password":password.get(), "okul":okul.get().lower(),"saat":saat.get()}

# extract config data from config.json
if os.path.exists(os.path.join(application_path,"configAtd.json")):
    config = json.load(open(os.path.join(application_path,"configAtD.json"), "r"))
else:
    config = getConfig()
    json.dump(config, open(os.path.join(application_path,"configAtd.json"), "w"))

sinifAdı = config["sinif"]
def kacıncı_ders():
    SAATLER = requests.get(f"http://{config['host']}:{config['port']}/saatler/{config['okul']}").json()
    SAATLER=[i.split("-") for i in SAATLER]
    SAATLER=[[datetime.datetime.strptime(i[0],"%H:%M"),datetime.datetime.strptime(i[1],"%H:%M")] for i in SAATLER]
    now= datetime.datetime.now().time()
    for i in SAATLER:
        if i[0].time()<=now<=i[1].time():
            nth_ders = SAATLER.index(i)
            dersBitimi = i[0]
            break
    return nth_ders,dersBitimi
nth_ders,dersBası=kacıncı_ders()

if os.path.exists(dataPath:= os.path.join(application_path,"data/known_faces_data.npz")):
    loaded_data = np.load(dataPath)
    known_faces_encodings = loaded_data["known_faces_encodings"]
    names = loaded_data['names']
else:
    known_faces_encodings, names = getFaceEncodings(getDersProg(sinifAdı,config["host"], config["port"], config["password"])[0][nth_ders],config["host"], config["port"], config["password"])
    if not os.path.exists(os.path.join(application_path,"data")):
        os.mkdir(os.path.join(application_path,"data"))
    np.savez(dataPath, **{"known_faces_encodings":known_faces_encodings, "names":names})
# Initialize the video capture
video_capture = cv2.VideoCapture(0)

faces_found=[]
text_shown=(0,"")
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
            text_shown=(time(),name)

        # Draw rectangle around the detected face
        top, right, bottom, left = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    if time()-text_shown[0]<2:
        cv2.putText(image, text_shown[1] + " yoklamaya kaydedildi", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    else:text_shown=(0,"")
    cv2.imshow('Face Recognition', image)

    if datetime.datetime.now()>datetime.timedelta(minutes=int(config["saat"]))+dersBası:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
video_capture.release()
cv2.destroyAllWindows()

faces_found_names = [row[0] for row in faces_found]

missing_names = [name for name in names if name not in faces_found_names]
print("Yoklamaya katılmayanlar:", ", ".join(missing_names))
if missing_names!=[]:
    text2speech("Yoklamaya katılmayanlar " + " ".join(missing_names))

def sendAtd(faces_found,missing_names, host, port, password):
    login = requests.get(f"http://{host}:{port}/login/{password}")
    if login.text == "Login successful!":
        print("Login successful!")
        r = requests.post(f"http://{host}:{port}/sendAtd",cookies=login.cookies,headers={"Content-Type": "application/json"},data=json.dumps([sinifAdı,faces_found,missing_names,nth_ders]))
        print(r.text)
if input("Yoklamayı göndermek ister misiniz? (e/h)")=="e":
    sendAtd(faces_found,missing_names, config["host"], config["port"], config["password"])
elif input("Tekrar yoklama almak ister misiniz? (e/h)")=="e":
    os.system("python " + os.path.join(application_path,"face_recog_atd.py"))