import datetime
from email.mime.text import MIMEText
import json
import os
import sqlite3
import sys
from time import sleep
from tkinter import messagebox
import requests

import smtplib, ssl
from email.mime.multipart import MIMEMultipart

import tkinter as tk

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

port = 465  # For SSL
context = ssl.create_default_context()
def getData():
    window = tk.Tk()
    # create three tk variables for email, password, and city
    email_var = tk.StringVar()
    password_var = tk.StringVar()
    city_var = tk.StringVar()
    # create three entry widgets for email, password, and city
    email_input = tk.Entry(window, textvariable=email_var)
    email_input.grid(row=0, column=1)
    password_input = tk.Entry(window, textvariable=password_var)
    password_input.grid(row=1, column=1)
    city_input = tk.Entry(window, textvariable=city_var)
    city_input.grid(row=2, column=1)
    # create three labels for email, password, and city
    email_label = tk.Label(window, text="E-posta:")
    email_label.grid(row=0, column=0, sticky="w")
    password_label = tk.Label(window, text="Şifre:")
    password_label.grid(row=1, column=0, sticky="w")
    city_label = tk.Label(window, text="Şehir:")
    city_label.grid(row=2, column=0, sticky="w")
    # create a button to save the data
    button = tk.Button(window, text="Kaydet", command=window.destroy)
    button.grid(row=3, column=1)
    window.mainloop()
    email = email_var.get()
    password = password_var.get()
    city = city_var.get()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(str(email), str(password))
        server.quit()
    if city == "" or email == "" or password == "" or city_var.get() == "":
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun")
        raise Exception("E-posta veya şifre boş!")
    return {"email": email, "password": password, "city": city}

if os.path.exists("configServer.json"):
    config = json.load(open("configServer.json", "r"))
else:
    config = getData()
    json.dump(config, open("configServer.json", "w"))

password = config["password"]
sender_email = config["email"]

city = config["city"]
eskiDeprem=0
def depremKontrol():
    global eskiDeprem
    # make a requst and get json data
    response = requests.get("https://api.orhanaydogdu.com.tr/deprem/live.php?limit=1")
    data = response.json()["result"]
    cities = data[0]["location_properties"]["closestCities"]
    in_city = city in [city["name"] for city in cities ]
    when = datetime.datetime.strptime(data[0]["date"], '%Y.%m.%d %H:%M:%S')
    happening_now = when > datetime.datetime.now() - datetime.timedelta(minutes=3)
    magnitude = data[0]["mag"]
    # print(datetime.datetime.strptime("2024.01.11 18:31:37", "%Y.%m.%d %H:%M:%S") - datetime.timedelta(minutes=3))
    if in_city and happening_now:
        if eskiDeprem==when:
            return False
        eskiDeprem=when
        for i in cities:
            if i["name"]==city:
                distance = i["distance"]/1000
        print(f"Deprem oldu! {magnitude} büyüklüğünde, {distance} km uzaklıkta.")
        if magnitude >= 3.5 and distance < 15:
            return True
        elif magnitude >= 5 and distance < 50:
            return True
        elif magnitude >= 6 and distance < 100:
            return True
        else: return False

def SQL2HTML():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('select adSoyad,sinif,kan from ogrenciler')
    personal_info = cursor.fetchall()
    personal_info_dic = cursor.description
    cursor.execute("SELECT enson FROM ogrgoruldu")
    enson = cursor.fetchall()
    enson_disc = cursor.description
    table_style = '''
    <style>
    table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
    td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
    tr:nth-child(even) {
        background-color: #dddddd;
        }
    </style>
    '''
    html=f'<html><head>{table_style}</head><body><table>' 
    html+='<tr>'
    for field in personal_info_dic+enson_disc:
        html += '<th>' + field[0] + '</th>'
    html+='</tr>'
    # print(list(zip(personal_info,enson)))
    l = [i+j for i,j in list(zip(personal_info,enson))]
    for row in l:
        html+='<tr>'
        for field in row:
            html += '<td>' + str(field) + '</td>'
        html+='</tr>'
    
    html+='</table></body></html>'
    conn.close()
    return html

receiver_emails = open(os.path.join(application_path,"receiver_emails.txt"), "r").read().split("\n")

message = MIMEMultipart("alternative")
message["Subject"] = "DEPREM!!!"
message["From"] = sender_email
message["To"] = ", ".join(receiver_emails)
text = "Bir deperm oldu."

def konrol():
    if(depremKontrol()):
        html = SQL2HTML()
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(config["email"], password)
            server.sendmail(sender_email, receiver_emails, message.as_string())
            server.quit()
        print("mail gönderildi")

while True: 
    konrol()
    sleep(60)