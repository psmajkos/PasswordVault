from tkinter import *
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import csv
from tkinter import *
from tkinter import filedialog
import mysql.connector
import csv
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
import tkinter.messagebox
from tkinter import ttk



def db_upload():
    window = Tk()

    def create_db():
        my_conn = create_engine('mysql+pymysql://root:Pcf85830@localhost:3306')
        my_conn.execute("""
        CREATE SCHEMA IF NOT EXISTS basement""")
    create_db()

    def browseFiles():
        filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Database file", "*.csv"), ("all files", "*.*")))
        label_file_explorer.configure(text="Database uploaded")

        engine = create_engine("mysql+pymysql://root:Pcf85830@localhost/basement")
        with open(filename, 'r') as file:
            data_df = pd.read_csv(file)
            data_df.to_sql('dane', con=engine, index=False, index_label='id', method='multi', if_exists='replace')


    label_file_explorer = Label(window, text = "Upload database from file", fg = "white")
    label_file_explorer.grid(column = 1, row = 1)
    button_explore = Button(window, text = "Browse Files", command = browseFiles)
  
    button_exit = Button(window, text = "Exit", command = exit)
    button_explore.grid(column = 1, row = 2)
  
    button_exit.grid(column = 1,row = 3)

    window.mainloop()

def db_backup():
    root = Tk()
    root.title("Database Backup")

    def browseFiles():
        # Connect to the MySQL database
        cnx = mysql.connector.connect(user='root', password='Pcf85830', host='localhost', database='basement')
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM dane")
        rows = cursor.fetchall()
        filename = asksaveasfile(mode='w',initialfile = 'db_backup.csv', defaultextension=".csv",filetypes=[("Database file","*.csv")])
        if filename is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        csvwriter = csv.writer(filename)
        csvwriter.writerow([i[0] for i in cursor.description]) # write headers
        csvwriter.writerows(rows)
        tkinter.messagebox.showinfo(title="Done", message="You successfully saved database backup!")

        filename.close() # `()` was missing.
        label_file_explorer.configure(text="File Opened: "+filename)

        cursor.close()
        cnx.close()

    label_file_explorer = Label(root, text = "Select the destination for your \n database backup", fg = "white")
    label_file_explorer.grid(column = 1, row = 1)

    button_explore = ttk.Button(root, text = "Open browser", command = browseFiles)
    button_exit = ttk.Button(root, text = "Exit", command = exit)

    button_explore.grid(column = 1, row = 2)
    button_exit.grid(column = 1,row = 3)
    # Close the cursor and the connection to the database

    root.mainloop()

