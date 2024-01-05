import datetime
import os
import sqlite3
import requests

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



city="İstanbul"
def depremKontrol():
    # make a requst and get json data
    response = requests.get("https://api.orhanaydogdu.com.tr/deprem/live.php?limit=1")
    data = response.json()["result"]
    cities = data[0]["location_properties"]["closestCities"]
    in_city = any([True for city in cities if city["name"] == city])
    when = datetime.datetime.strptime(data[0]["date"], '%Y.%m.%d %H:%M:%S')
    happening_now = when > datetime.datetime.now() - datetime.timedelta(minutes=3)
    magnitude = data[0]["mag"]
    
    if in_city and happening_now and magnitude >= 2.5:
        for i in cities:
            if i["name"]==city:
                distance = i["distance"]/1000
                
        if magnitude >= 3.5 and distance < 15:
            return True
        elif magnitude >= 5 and distance < 50:
            return True
        elif magnitude >= 6 and distance < 100:
            return True
        else: return False

def SQL2HTML(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('select * from my_table')
    html='<html><body><table>' 
    html+='<tr>'
    for field in cursor.description:
        html += '<th>' + field[0] + '</th>'
    html+='</tr>'
    for row in cursor.fetchall():
        html+='<tr>'
        for field in row:
            html += '<td>' + str(field) + '</td>'
        html+='</tr>'
    html+='</table></body></html>'
    conn.close()
    return html

port = 465  # For SSL
password = os.environ.get('EMAIL_PASSWORD')
context = ssl.create_default_context()
sender_email = "raspi9600@gmail.com"
receiver_emails = ["efecaliskan08@gmail.com","raspi9600@gmail.com"]

message = MIMEMultipart("alternative")
message["Subject"] = "DEPREM!!!"
message["From"] = sender_email
message["To"] = ", ".join(receiver_emails)
text = "Bir deperm oldu."

def konrol():
    if(depremKontrol()):
        html = SQL2HTML("./my_database.db")
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("raspi9600@gmail.com", password)
            server.sendmail(sender_email, receiver_emails, message.as_string())
      
konrol()