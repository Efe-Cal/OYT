import datetime
from requsetData import getFaceEncodings
from serverSideInput import getConfig
import json
import os
import sys
import cv2
import face_recognition
import numpy as np
from time import time
import requests
import datetime
from email.mime.text import MIMEText
import json
from time import sleep
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from serverSideInput import getData
from email.mime.image import MIMEImage



if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
if os.path.exists(os.path.join(application_path,"configAtd.json")):
    config = json.load(open(os.path.join(application_path,"configAtD.json"), "r"))
else:
    config = getConfig()
    json.dump(config, open(os.path.join(application_path,"configAtd.json"), "w"))
              

known_faces_encodings, names = getFaceEncodings("all",config["host"], config["port"], config["password"])

port = 465  # For SSL
context = ssl.create_default_context()

# Load configuration
config = json.load(open("configServer.json", "r"))

email_password = config["email_password"]
sender_email = config["email"]
receiver_emails = open("receiver_emails.txt", "r").read().split("\n")

def send_email(subject, text):
    with open("image.jpg", 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename("image.jpg"))
    

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    
    message.attach(MIMEText(text, "plain"))
    message.attach(image) 
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_emails, message.as_string())


def kacıncı_ders():
    SAATLER = requests.get(f"http://{config['host']}:{config['port']}/saatler/{config['okul']}")[0]
    SAATLER=[i.split("-") for i in SAATLER]
    SAATLER=[[datetime.datetime.strptime(i[0],"%H:%M"),datetime.datetime.strptime(i[1],"%H:%M")] for i in SAATLER]
    now=datetime.datetime.now().time()
    nth_ders,dersBitimi=-1,-1
    for i in SAATLER:
        if i[0].time()<=now<=i[1].time():
            nth_ders = SAATLER.index(i)
            dersBitimi = i[0]
            break
    return nth_ders,dersBitimi


video_capture = cv2.VideoCapture(0)

login = requests.get(f"http://{config['host']}:{config['port']}/login/{config['password']}")
wait = False
while True:
    ret, image = video_capture.read()
    rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    cam_face_locations = face_recognition.face_locations(rgb_frame)
    cam_face_encodings = face_recognition.face_encodings(rgb_frame, cam_face_locations)


    for face_encoding, face_location in zip(cam_face_encodings, cam_face_locations):
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        name = ""

        if True in matches:
            wait = True
            name = names[matches.index(True)]
            [name,datetime.datetime.now().strftime("%H.%M")]
            if kacıncı_ders()[0] == -1:
              requests.get(f"http://{config['host']}:{config['port']}/kacak/{name}/\
                          {datetime.datetime.now().strftime('%H.%M')}",cookies=login.cookies,headers=login.headers)
        else:
            cv2.imwrite("image.jpg", image)
            send_email("YABANCI VAR",f"{config['sinif']}'da birisi var")
            



        top, right, bottom, left = face_location
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(image, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow('Face Recognition', image)
    if wait:
        sleep(60)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video_capture.release()
cv2.destroyAllWindows()




