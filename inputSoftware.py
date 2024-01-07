import tkinter as tk
from tkinter import filedialog
import tkinterDnD

def browse_file():
    file_path = filedialog.askopenfilename()
    file_input.delete(0, tk.END)
    file_input.insert(tk.END, file_path)

def submit():
    adSoyad = input1.get()
    sinif = input2.get()
    kan = input3.get()
    file_path = file_input.get()
    # change cursor to a watch and disable all controls
    window.config(cursor="watch")
    submit_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    # --------------------------------------------------
    #       Database & Face Recognition operations
    # --------------------------------------------------
    # reset the cursor and controls
    window.config(cursor="")
    submit_button.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)
    
    # clear the form
    input1.delete(0, tk.END)
    input2.delete(0, tk.END)
    input3.set("Kan grubu seçin")
    file_input.delete(0, tk.END)

window = tkinterDnD.Tk() 
window.title("Öğrenci Bilgi Sistemi") 
window.geometry("400x200")  # Set the window size

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

file_label = tk.Label(form_frame, text="Fotoğraf:")
file_label.grid(row=3, column=0, sticky="w")


def drop(event):
    # This function is called, when stuff is dropped into a widget
    file_input.delete(0, tk.END)
    file_input.insert(0,event.data)
def drag_command(event):
    # This function is called at the start of the drag,
    # it returns the drag type, the content type, and the actual content
    return (tkinterDnD.COPY, "DND_Text", "Some nice dropped text!")


file_input = tk.Entry(form_frame)
file_input.grid(row=3, column=1, pady=10)

form_frame.register_drop_target("*")
form_frame.bind("<<Drop:File>>", drop)
form_frame.register_drag_source("DND_Files")
form_frame.bind("<<DragInitCmd>>", drag_command)

browse_button = tk.Button(form_frame, text="Göz at", command=browse_file)
browse_button.grid(row=3, column=2, padx=10)

submit_button = tk.Button(form_frame, text="Kaydet", command=submit)
submit_button.grid(row=4, column=1, pady=10)

window.mainloop()

