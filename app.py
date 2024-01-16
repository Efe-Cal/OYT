# Import the Flask and Flask-Login libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import sys
from flask import Flask, render_template, request, session, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os
import sqlite3
import json
from serverSideInput import getData

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)


if os.path.exists(os.path.join(application_path,"configServer.json")):
    config = json.load(open(os.path.join(application_path,"configServer.json"), "r"))
else:
    config = getData()
    json.dump(config, open(os.path.join(application_path,"configServer.json"), "w"))



# Create a Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = "01239jlgado"

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define a User model
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return user if user.get_id() == user_id else None


# Create a user
user = User('asdf', '123')

# Register the user with Flask-Login
login_manager.user_loader(load_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        # Get the username and password from the request
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are valid
        if user.username == username and user.password == password:
            # Login the user
            login_user(user)
            return redirect('/')

        # Otherwise, show an error message
        return render_template('login.html', error='YANLIŞ')

    # Render the login form for GET requests
    return render_template('login.html')

# Define a route for the logout page
@app.route('/logout')
def logout():
    # Logout the user
    logout_user()
    return redirect('/login')

# Define a protected route
@app.route('/')
@login_required
def protected():
    return render_template('protected.html')


def get_table_data():
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    cursor.execute('SELECT adSoyad,sinif,kan,vEmail,ozelSaglıkDurumu FROM ogrenciler')  # Replace 'your_table' with your table name
    data_from_table = cursor.fetchall()
    
    cursor.execute('SELECT enson FROM ogrgoruldu')  # Assuming 'ogrgoruldu' is the table name and 'enson' is the column name
    data_from_ogrgoruldu = cursor.fetchall()

    conn.close()
    return data_from_table, data_from_ogrgoruldu

def ogrbull():
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    input_valu = request.form.get('in1')

    input_value = input_valu.split(',')
    datas = []
    datass = []
    for i in input_value:
        if cursor.execute('SELECT adSoyad,sinif,kan,vEmail,ozelSaglıkDurumu FROM ogrenciler WHERE adSoyad = ?',(i,)):
            datas1 = cursor.fetchall()
            datas.append(datas1[0])
    print(datas)
    print()
    for i in input_value:
        if cursor.execute('SELECT enson FROM ogrgoruldu WHERE ogrisim = ?',(i,)):
            datass1 = cursor.fetchall()
            datass.append(datass1[0])

    return datas,datass

receiver_emails = open(os.path.join(application_path,"receiver_emails.txt"), "r").read().split("\n")
port = 465  # For SSL
context = ssl.create_default_context()
email_password = config["email_password"]
sender_email = config["email"]
message = MIMEMultipart("alternative")
message["Subject"] = "DEPREM!!!"
message["From"] = sender_email
message["To"] = ", ".join(receiver_emails)
text = "ACIL DURUM BUTONU BASILDI"

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect("/login")

@app.route('/acildurum')
def acil():
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    cursor.execute('select adSoyad,sinif,kan,ozelSaglıkDurumu from ogrenciler')
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
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config["email"], email_password)
        server.sendmail(sender_email, receiver_emails, message.as_string())
        server.quit()
    return redirect('/')


def sinifbull():
    conn = sqlite3.connect(os.path.join(application_path,"database.db"))
    cursor = conn.cursor()
    input_valu = request.form.get('in1')


    cursor.execute('SELECT adSoyad,sinif,kan,vEmail,ozelSaglıkDurumu FROM ogrenciler WHERE sinif = ?',(input_valu,))
    datas = cursor.fetchall()
    datass = []
    for i in datas:
        i = i[0]
        print(i)
        if cursor.execute('SELECT enson FROM ogrgoruldu WHERE ogrisim = ?',(i,)):
            datass1 = cursor.fetchall()
            datass.append(datass1)
    print(datass)
    return datas, datass

@app.route('/results', methods=['POST'])
@login_required
def handle_form(): 
    button_clicked = request.form['buton']

    if button_clicked == '1':
        # Handle Tüm Liste button click
        # Perform actions for Tüm Liste
        data_table, data_ogrgoruldu = get_table_data()
        return render_template('results.html', data_table=data_table, data_ogrgoruldu=data_ogrgoruldu)
    
    elif button_clicked == '2':
        datas, datass = ogrbull()
        return render_template("ogrbul.html", datas = datas, datass = datass)

    elif button_clicked == '3':
        datas, datass = sinifbull()
        return render_template("sinifbul.html", datas = datas, datass = datass)

    return "Unknown action"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

