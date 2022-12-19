import tkinter
from tkinter import ttk
from tkinter import messagebox
import secrets, string
from tkinter import *

root = tkinter.Tk()
root.title("Password Generator")

pas_var=IntVar()
pas_var.set("")

letters = string.ascii_letters
digits = string.digits
special_chars = string.punctuation

alphabet = letters + digits + special_chars

def passgen():
    pwd_length = pas_var.get()
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))
    pas_entry.delete(0, END)
    pas_entry.insert(0,pwd)

    # copy_button = ttk.Button(root, text="copy to clipboard", command=copy_pass)
    # copy_button.grid(column=1, row=1)

    # def copy_pass():
    #     root.clipboard_clear()
    #     root.clipboard_append(pwd)

text = ttk.Label(root, text="Enter the length of your password: ")
button = ttk.Button(root, text="Do it bitch", command=passgen)
pas_entry = ttk.Entry(root, textvariable=pas_var)

text.grid(column=0, row=0)
button.grid(column=0, row=1)
pas_entry.grid(column=1, row=0)

root.mainloop()