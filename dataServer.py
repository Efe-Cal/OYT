import datetime
import os
import queue
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import sys
from time import sleep
from flask import Flask, jsonify, request
from flask_login import LoginManager, UserMixin, login_required, login_user,logout_user
from face_recognition_methods import load_faces
import json
import threading

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

config = json.load(open("server_cfg.json", "r"))
# Dummy user credentials
PASSWORD = config["password"]

# User class for Flask-Login
class User(UserMixin):
    pass

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # In this example, we only have one user
        user = User()
        user.id = user_id
        return user

@app.route('/login/<password>', methods=['GET'])
def login(password):
    if str(password) == PASSWORD:
        user = User()
        user.id = 1
        login_user(user)  # Login the user
        return 'Login successful!'
    else:
        return 'Invalid password'

@app.route('/getFaceEncodings/<sinif>')
@login_required  # Protect the route
def protected(sinif):
    data = load_faces(sinif)
    data[0] = [i.tolist() for i in data[0]]
    return jsonify(data)

@app.route('/dersprog/<sinif>')
@login_required  # Protect the route
def dersprog(sinif):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM dersprog WHERE sinif='{sinif}'")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/logout')
@login_required  # Protect the route
def logout():
    logout_user()
    return 'Logged out successfully!'
q = queue.Queue()
@app.route('/sendAtd',methods=['POST'])
def sendAtd():
    data = request.get_json()
    q.put(data)
    return "OK"

# @app.route("/saatler/<okul>")
# def saatler(okul):
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT * FROM saatler WHERE okul='{okul}'")
#     data = cursor.fetchall()
#     return jsonify(data)


olmayanlar = []

port = 465  # For SSL
password = os.environ.get('EMAIL_PASSWORD')
context = ssl.create_default_context()
sender_email = "raspi9600@gmail.com"
receiver_emails = ["nkadayifci@cevrekoleji.k12.tr"]

message = MIMEMultipart("alternative")
message["Subject"] = "YOKLAMA!!!"
message["From"] = sender_email
message["To"] = ", ".join(receiver_emails)
def mailAt():
    global olmayanlar
    text = "Yoklama alındı."
    while datetime.datetime.now().time()<datetime.datetime.strptime("08:30", "%H:%M").time():
        sleep(60)
    for i in olmayanlar:
        print(i)
        text += "\n" + i
    message.attach(MIMEText(text, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("raspi9600@gmail.com", password)
        server.sendmail(sender_email, receiver_emails, message.as_string())

def yoklama_al():
    global olmayanlar
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    while True:
        if q.empty():
            continue
        data = q.get()
        faces_found = data[1]
        missing_names = data[2]
        nth_ders = data[3]
        olmayanlar+=missing_names
        # insert missing_names to database
        for name in faces_found:
            cursor.execute(f"UPDATE ogrgoruldu SET d{nth_ders+1}='{data[0]}' WHERE ogrisim='{name[0]}'")
            cursor.execute(f"UPDATE ogrgoruldu SET enson='{data[0]},{name[1]}' WHERE ogrisim='{name[0]}'")
        conn.commit()
        conn.close()

if __name__ == '__main__':
    t = threading.Thread(target=yoklama_al)
    t.start()
    t2 = threading.Thread(target=mailAt)
    t2.start()
    app.run(port=7777,debug=True)
