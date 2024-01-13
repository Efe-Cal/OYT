import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinterDnD
import sqlite3
import numpy as np
import io
from face_recognition_methods import encode_image
import os, sys

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image File", ".jpg")])
    file_input.delete(0, tk.END)
    file_input.insert(tk.END, file_path)

def submit():
    adSoyad = input1.get()
    sinif = input2.get()
    kan = input3.get()
    vEmail = email_input.get()
    file_path = file_input.get()
    saglıkDurumu = input4.get()
    if adSoyad == "" or sinif == "" or len(kan)>3 or vEmail == "" or file_path == "":
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun")
        return
    # change cursor to a watch and disable all controls
    window.config(cursor="watch")
    submit_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    
    face_encode = encode_image(file_path)
    
    conn = sqlite3.connect(os.path.join(application_path,"database.db"), detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ogrenciler (adSoyad TEXT, sinif TEXT, kan TEXT, vEmail TEXT, face_encode array, ozelSaglıkDurumu TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS 'ogrgoruldu' ('ogrisim' TEXT NOT NULL,'d1' TEXT DEFAULT NULL,'d2' TEXT DEFAULT NULL,'d3' TEXT DEFAULT NULL,'d4' TEXT DEFAULT NULL,'d5' TEXT DEFAULT NULL,'d6' TEXT DEFAULT NULL,'d7' TEXT DEFAULT NULL,'d8' TEXT DEFAULT NULL,'d9' TEXT DEFAULT NULL,'d10' TEXT DEFAULT NULL,PRIMARY KEY ('ogrisim'))")
    cursor.execute("INSERT INTO ogrenciler (adSoyad, sinif, kan, vEmail, face_encode) VALUES (?, ?, ?, ?, ?)", (adSoyad, sinif, kan, vEmail,face_encode))
    cursor.execute("INSERT INTO ogrgoruldu (ogrisim) VALUES (?)", (adSoyad,))
    conn.commit()
    conn.close()

    # reset the cursor and controls
    window.config(cursor="")
    submit_button.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)
    
    # clear the form
    input1.delete(0, tk.END)
    input2.delete(0, tk.END)
    input3.set("Kan grubu seçin")
    email_input.delete(0, tk.END)
    file_input.delete(0, tk.END)

window = tkinterDnD.Tk() 
window.title("Öğrenci Bilgi Sistemi") 
window.geometry("400x300")  # Set the window size
window.resizable(False, False)  # Disable resizing the window

# Create a frame for the form
form_frame = tk.Frame(window)
form_frame.pack(padx=20, pady=20)

# Create labels and entries for the form
label1 = tk.Label(form_frame, text="Ad ve Soyad:")
label1.grid(row=0, column=0, sticky="w")
input1 = tk.Entry(form_frame)
input1.grid(row=0, column=1)

label2 = tk.Label(form_frame, text="Sınıf:")
label2.grid(row=1, column=0, sticky="w")
input2 = tk.Entry(form_frame)
input2.grid(row=1, column=1)

label3 = tk.Label(form_frame, text="Kan grubu:")
label3.grid(row=2, column=0, sticky="w")
input3 = tk.StringVar()
input3.set("Kan grubu seçin")

dropdown = tk.OptionMenu(form_frame, input3, "A+", "A-", "B+", "B-", "AB+", "AB-", "0+", "0-")
dropdown.grid(row=2, column=1)

email_label = tk.Label(form_frame, text="Veli E-posta:")
email_label.grid(row=3, column=0, sticky="w")
email_input = tk.Entry(form_frame)
email_input.grid(row=3, column=1)

input4 = tk.StringVar()
input4.set("Özel Sağlık Durumu")
label4 = tk.Label(form_frame, text="Özel Sağlık Durumu:")
label4.grid(row=4, column=0, sticky="w")
text_box = tk.Text(form_frame, height=5, width=20)
text_box.grid(row=4, column=1)



file_label = tk.Label(form_frame, text="Öğrencinin Fotoğrafı:")
file_label.grid(row=5, column=0, sticky="w")


def drop(event):
    # This function is called, when stuff is dropped into a widget
    file_input.delete(0, tk.END)
    file_input.insert(0,event.data)
def drag_command(event):
    # This function is called at the start of the drag,
    # it returns the drag type, the content type, and the actual content
    return (tkinterDnD.COPY, "DND_Text", "Some nice dropped text!")


file_input = tk.Entry(form_frame)
file_input.grid(row=5, column=1, pady=10)

form_frame.register_drop_target("*")
form_frame.bind("<<Drop:File>>", drop)
form_frame.register_drag_source("DND_Files")
form_frame.bind("<<DragInitCmd>>", drag_command)

browse_button = tk.Button(form_frame, text="Göz at", command=browse_file)
browse_button.grid(row=5, column=2, padx=10)

submit_button = tk.Button(form_frame, text="Kaydet", command=submit)
submit_button.grid(row=6, column=1, pady=10)

window.mainloop()

