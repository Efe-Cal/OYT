import tkinter as tk
import smtplib, ssl
from tkinter import messagebox

port = 465  # For SSL
context = ssl.create_default_context()
def getData():
    window = tk.Tk()
    window.title("Ayarlar")
    window.eval('tk::PlaceWindow . center')
    # create three tk variables for email, password, and city
    email_var = tk.StringVar()
    email_password_var = tk.StringVar()
    city_var = tk.StringVar()
    server_password_var = tk.StringVar()
    # create three entry widgets for email, password, and city
    email_input = tk.Entry(window, textvariable=email_var)
    email_input.grid(row=0, column=1)
    email_password_input = tk.Entry(window, textvariable=email_password_var)
    email_password_input.grid(row=1, column=1)
    server_password_input = tk.Entry(window, textvariable=server_password_var)
    server_password_input.grid(row=2, column=1)
    city_input = tk.Entry(window, textvariable=city_var)
    city_input.grid(row=3, column=1)
    # create three labels for email, password, and city
    email_label = tk.Label(window, text="E-posta:")
    email_label.grid(row=0, column=0, sticky="w")
    email_password_label = tk.Label(window, text="E-posta Şifresi:")
    email_password_label.grid(row=1, column=0, sticky="w")
    server_password_label = tk.Label(window, text="Sunucu Şifresi:")
    server_password_label.grid(row=2, column=0, sticky="w")
    city_label = tk.Label(window, text="Şehir:")
    city_label.grid(row=3, column=0, sticky="w")
    # create a button to save the data
    button = tk.Button(window, text="Kaydet", command=window.destroy)
    button.grid(row=4, column=1)
    window.mainloop()
    email = email_var.get()
    password = email_password_var.get()
    city = city_var.get()
    if city == "" or email == "" or password == "" or city_var.get() == "":
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
        raise Exception("E-posta veya şifre boş!")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(str(email), str(password))
        server.quit()
    return {"email": email, "email_password": password, "city": city,"password":server_password_var.get()}
