import datetime
import functools
import os
import queue
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import sys
from time import sleep
from flask import Flask, g, jsonify, request, session
from face_recognition_methods import load_faces
import json
import threading
from serverSideInput import getData

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

port = 465  # For SSL
context = ssl.create_default_context()

if os.path.exists(os.path.join(application_path,"configServer.json")):
    config = json.load(open(os.path.join(application_path,"configServer.json"), "r"))
else:
    config = getData()
    json.dump(config, open(os.path.join(application_path,"configServer.json"), "w"))
# Dummy user credentials
PASSWORD = config["password"]

@app.route('/login/<password>', methods=['GET'])
def login(password):
    error = None

    if not config['password']==password:
        error = 'Incorrect password.'
        return error
    if error is None:
        session.clear()
        session['user_id'] = request.remote_addr

    return 'Login successful!'

def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = request.remote_addr
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return "Login required!"

        return view(**kwargs)

    return wrapped_view
@app.before_request
def before_request():
    load_logged_in_user()

@app.route('/getFaceEncodings/<sinif>')
@login_required  # Protect the route
def protected(sinif):
    data = load_faces(sinif)
    data[0] = [i.tolist() for i in data[0]]
    return jsonify(data)

@app.route('/dersprog/<sinif>')
@login_required  # Protect the route
def dersprog(sinif):
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM dersprog WHERE sinif='{sinif}'")
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/logout')
def logout():
    session.clear()
    return "Logged out!"

q = queue.Queue()
@app.route('/sendAtd',methods=['POST'])
def sendAtd():
    data = request.get_json()
    q.put(data)
    return "OK"

@app.route("/saatler/<okul>")
def saatler(okul):
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM saatler WHERE okul='{okul}'")
    data = cursor.fetchall()
    return jsonify(data)

olmayanlar = []

email_password = config["email_password"]
sender_email = config["email"]
receiver_emails = open(os.path.join(application_path,"receiver_emails.txt"), "r").read().split("\n")

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
        server.login(sender_email, email_password)
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
    app.run("0.0.0.0",port=7777,debug=True)
