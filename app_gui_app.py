from tkinter import Tk, Label, StringVar, ttk, CENTER, LEFT, HORIZONTAL, X
import tkinter  as tk 
from tkinter import messagebox as msg
import pyperclip
#from backup import db_upload, db_backup
import json
from cryptography.fernet import Fernet
import hashlib
import sqlite3
import wmi

def get_hwid():
    c = wmi.WMI()
    # Get the hardware ID of the first disk drive
    for disk in c.Win32_DiskDrive():
        return disk.SerialNumber.strip()
hwid = get_hwid()
# print("Hardware ID:", hwid)


# read the key from a file
with open('key.key', 'rb') as key_file:
    key = key_file.read()

fernet = Fernet(key)

#Creating Connection and database
def get_conn():
    return sqlite3.connect("basement.db")

#Creating tables in database
my_conn = get_conn()
my_conn.execute('''CREATE TABLE IF NOT EXISTS hwid
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                hwid varchar(300) NOT NULL)''')

my_conn.execute('''CREATE TABLE IF NOT EXISTS password
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                password varchar(300) NOT NULL)''')

my_conn.execute('''CREATE TABLE IF NOT EXISTS dane
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform varchar(45) NOT NULL,
                login varchar(45) NOT NULL,
                password varchar(300) NOT NULL)''')


def insert_hwid():
    my_conn = get_conn()

    insert_query = """INSERT INTO hwid(hwid) VALUES (?)"""
    vals = (hwid,)
    my_conn.execute(insert_query,vals)
    my_conn.commit()
insert_hwid()

#Function to make main window
def main():
    root = Tk()
    root.title("Vault")
    root.geometry("850x350")
    root.resizable(False, False)
    root.minsize(850, 350)   # Lock the minimum size of the window
    root.maxsize(850, 350)   # Lock the maximum size of the window

    my_conn = get_conn()
    display = ttk.Frame(root)

    canvas = tk.Canvas(root, width=900, height=300)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Create a frame widget inside the canvas widget to hold the rows of data
    frame = tk.Frame(canvas)

    # Configure the canvas widget to use the scrollbar widget
    canvas.configure(yscrollcommand=scrollbar.set)

    # Add the frame widget to the canvas widget
    canvas.create_window((0, 0), window=frame, anchor="nw")

    # Add the canvas widget 
    canvas.pack(side="left", fill="both", expand=True)
    canvas.place(x=0, y=0)
    scrollbar.pack(side="right", fill="both")

    def create_master_password():
        mstr_label = ttk.Label(root, text="Create Master Password", font=('verdana',12))
        mstr_entry = ttk.Entry(root, show="*", font=('verdana',12))
        mstr_label_retype = ttk.Label(root, text="Retype Password", font=('verdana',12))
        mstr_entry_retype = ttk.Entry(root, show="*", font=('verdana',12))
        info_label = ttk.Label(root, text="""*Type password to create a new main password, then press "Enter". You will be using it to login to application""")

        mstr_label.pack(pady=20)
        mstr_entry.pack(pady=20)
        mstr_entry.focus()
        mstr_label_retype.pack(pady=20)
        mstr_entry_retype.pack(pady=20)
        info_label.pack(pady=40)

        def save_password():
            if mstr_entry.get() == mstr_entry_retype.get():
                if len(mstr_entry.get()) < 6:
                    mstr_label.config(text="Password must be at least 6 characters long")
                    return
                my_conn = get_conn()
                hash = hashlib.sha512()
                hash.update(mstr_entry.get().encode())
                hash_hex = hash.hexdigest()

                insert_query = """INSERT INTO password(password) VALUES (?)"""
                vals = (hash_hex,)
                my_conn.execute(insert_query,vals)
                my_conn.commit()
                mstr_label.destroy()
                mstr_entry.destroy()
                mstr_entry.destroy()
                mstr_label_retype.destroy()
                mstr_entry_retype.destroy()
                info_label.destroy()
                root.update_idletasks()
                my_show()
            else:
                mstr_label.config(text="Passwords don't match")

        root.bind('<Return>', lambda event=None: save_password())

    def loginscreen():
        login_label = ttk.Label(root, text="Enter your password", font=('verdana',16))
        login_entry = ttk.Entry(root, show="*", font=('verdana',16))
        login_entry.focus()

        info_label_login = ttk.Label(root, text="""*Type your password and press "Enter" to log in to app.""")

        login_label.pack(pady=50)
        login_entry.pack()
        info_label_login.pack(pady=40)

        def login():
            hwid_check = my_conn.execute('SELECT hwid FROM hwid')
            hwid_matched = False
            for hw in hwid_check:
                if hwid == hw[0]:
                    hwid_matched = True
                    break

            if hwid_matched:
                p_set = my_conn.execute('SELECT password FROM password')
                hash = hashlib.sha512()
                hash.update(login_entry.get().encode())
                hash_hex = hash.hexdigest()
                password_matched = False
                for password in p_set:
                    if hash_hex == password[0]:
                        password_matched = True
                        break
                if password_matched:
                    #root.destroy()
                    login_entry.destroy()
                    login_label.destroy()
                    info_label_login.destroy()
                    root.update_idletasks()
                    my_show()
                else:
                    login_label.configure(text="Retype password")
                    login_entry.delete(0, tk.END)
            else:
                login_label.configure(text = "Wrong computer")
        root.bind('<Return>', lambda event=None: login())


    my_conn = get_conn()
    login_pass = my_conn.execute("""SELECT password FROM password""").fetchone()
    if login_pass is None:
        create_master_password()
    else:
        loginscreen()

    # Function to display rows from database
    def my_show():
        no = tk.Label(frame, width=8, text="No.")
        no.grid(row=0, column=0)
        site = tk.Label(frame,width=20, text="Site:")
        site.grid(row=0, column=1)
        login = tk.Label(frame,width=20, text="Login:")
        login.grid(row=0, column=2)
        password = tk.Label(frame,width=35, text="Password:")
        password.grid(row=0, column=3)
        

        ttk.Separator(frame, orient=HORIZONTAL, style='blue.TSeparator', class_= ttk.Separator,
        takefocus= 1, cursor='plus').grid(row=1, columnspan=20, pady=15, padx=25, sticky="nsew")
        main_buttons()
        for w in display.grid_slaves(): # remove all rows first 
            w.grid_forget() # remove rows 
        
        # Function to enumerate all rows
        p_set= my_conn.execute('SELECT login FROM dane')
        b=0
        index = 1
        for login in p_set:
            for k in range(len(login)):
                e=tk.Label(frame, width=8,fg='black',text=f'{index}',
                anchor='center')
                e.grid(row=b+2,column=k)

            index += 1
            b=b+1
    # Add the rows of data to the frame widget
        r_set = my_conn.execute('SELECT id, platform, login, password FROM dane')
        for i, student in enumerate(r_set):
            for j in range(1,len(student)):
                e=tk.Label(frame,width=20,fg='black',text=student[j],
                anchor='center')
                e.grid(row=i+2,column=j)

            b = StringVar()
            b.set("*******")
            for j in range(3,len(student)):
                b=tk.Entry(frame,width=35,fg='white',show="*", bg='purple', justify=CENTER,highlightthickness=0, borderwidth=0, textvariable=b)
                b.grid(row=i+2,column=j, padx=48)

            delete_button = ttk.Button(frame, text='Delete', width=8, command=lambda d=student[0], n=student[1]: my_delete(d, n))
            delete_button.grid(row=i+2, column=len(student)+2)
            copy_button = ttk.Button(frame, text='Copy', width=7, command=lambda id=student[0], name=student[1]: my_copy(id, name))
            copy_button.grid(row=i+2, column=5)
            edit_button = ttk.Button(frame, text='Edit', width=6, command=lambda id=student[0], name=student[1]: my_edit(id, name))
            edit_button.grid(row=i+2, column=7)


        # Update the scroll region of the canvas widget
        frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def my_edit(id,name):
        my_var=msg.askyesnocancel("Edit?",\
        "Edit" + ' ' + name + '?', icon='warning',default='no')
        if my_var:
            insert = Tk()
            insert.title("Insert Data")
            insert.resizable(False, False)
            my_conn = get_conn()
            bkg = "#636e72"

            frame = tk.Frame(insert, bg=bkg)
            site_label = tk.Label(frame, text="Platform: ", font=('verdana',12), bg=bkg)
            n = StringVar()
            n = set()
            site_entry = ttk.Combobox(frame, textvariable=n)
            # Here is saved sites 
            with open('sites_json.json', 'r') as file:
                sites = json.load(file)
                for site in sites:
                    site_entry['values'] = sites['site_name']
            login_label = tk.Label(frame, text="Login: ", font=('verdana',12), bg=bkg)
            login_entry = tk.Entry(frame, font=('verdana',12))

            password_label = tk.Label(frame, text="Password: ", font=('verdana',12), bg=bkg)
            password_entry = tk.Entry(frame, font=('verdana',12))

            # Funtion to insert a new record
            def editData():
                site = site_entry.get()
                login = login_entry.get()
                message = password_entry.get()
                putted_password = message.encode('utf-8')

                # encrypt the message
                encrypted_message = fernet.encrypt(putted_password)

                # print the encrypted message as a string
                password = encrypted_message.decode()

                update_query = """UPDATE dane
                SET platform = ?, login = ?, password = ?
                WHERE id = ?;
                """

                vals = (site, login, password, id) #password
                my_conn.execute(update_query,vals)
                my_conn.commit()
                msg.showinfo(title=None, message="Account edited successfully")
                insert.destroy()
                refresh()

        insert.bind('<Return>', lambda event=None: editData())

        site_label.grid(row=0, column=0)
        site_entry.grid(row=0, column=1, pady=10, padx=10)
        login_label.grid(row=1, column=0)
        login_entry.grid(row=1, column=1, pady=10, padx=10)
        password_label.grid(row=2, column=0, sticky='e')
        password_entry.grid(row=2, column=1, pady=10, padx=10)
        frame.grid(row=0, column=0)
        #my_show()
        insert.mainloop()
        insert.update()

    # Function to deleted selected row from database 
    def my_delete(id,name):
        my_var=msg.askyesno("Delete?",\
            "Delete" + ' ' + name + '?', icon='warning',default='no')
        if my_var:
            my_conn.execute('DELETE FROM dane WHERE id = ?', (id,))
            my_conn.commit()
            
            msg.showinfo("Deleted","Record Deleted")
            refresh()
            #my_show()

    def my_copy(id, name):
        my_var=msg.askyesnocancel("Copy?",\
            "Copy password of" + ' ' + name + '?', icon='info',default='no')
        if my_var:
            query = my_conn.execute("SELECT password FROM dane WHERE id ="+str(id))
            record = query.fetchone()

            for item in record:
                fernet = Fernet(key)
                message = item
                encrypted_message = message.encode('utf-8')

                # decrypt the message
                decrypted_message = fernet.decrypt(encrypted_message)
                decrypted = decrypted_message.decode()

                pyperclip.copy(decrypted)
                msg.showinfo(title=None, message="Copied to clipboard: " + decrypted)

    # Funtion to refresh all records from database
    def refresh():
        # Remove the old widgets from the frame
        for widget in frame.winfo_children():
            widget.destroy()
        frame.update_idletasks()
        display.update()
        my_show()
    display.pack(fill='both', anchor=CENTER, side='top', expand='1')
    #my_show()

    # Funtion to insert a new record(window)
    def applytodb():
        insert = Tk()
        insert.title("Insert Data")
        my_conn = get_conn()
        #c = connection.cursor()
        bkg = "#636e72"

        frame = tk.Frame(insert, bg=bkg)
        site_label = tk.Label(frame, text="Platform: ", font=('verdana',12), bg=bkg)
        n = StringVar()
        n = set()
        site_combo = ttk.Combobox(frame, textvariable=n)
        site_combo.set("Facebook")
        # Here is saved sites 
        with open('sites_json.json', 'r') as file:
            sites = json.load(file)
            for site in sites:
                site_combo['values'] = sites['site_name']
        login_label = tk.Label(frame, text="Login: ", font=('verdana',12), bg=bkg)
        login_entry = tk.Entry(frame, font=('verdana',12))

        password_label = tk.Label(frame, text="Password: ", font=('verdana',12), bg=bkg)
        password_entry = tk.Entry(frame, font=('verdana',12))

        # Funtion to insert a new record
        def insertData():
            site = site_combo.get()
            login = login_entry.get()
            message = password_entry.get()
            putted_password = message.encode('utf-8')

            # encrypt the message
            encrypted_message = fernet.encrypt(putted_password)

            # print the encrypted message as a string
            password = encrypted_message.decode()

            insert_query = """INSERT INTO dane(platform, login, password) VALUES (?,?,?)"""
            vals = (site, login, password,) #password
            my_conn.execute(insert_query,vals)
            my_conn.commit()
            msg.showinfo(title=None, message="Account added successfully")
            insert.destroy()
            refresh()

        insert.bind('<Return>', lambda event=None: insertData())

        site_label.grid(row=0, column=0)
        site_combo.grid(row=0, column=1, pady=10, padx=10)
        login_label.grid(row=1, column=0)
        login_entry.grid(row=1, column=1, pady=10, padx=10)
        password_label.grid(row=2, column=0, sticky='e')
        password_entry.grid(row=2, column=1, pady=10, padx=10)
        frame.grid(row=0, column=0)
        insert.mainloop()
        insert.update()
    
    def main_buttons():
        app = ttk.Frame(root, width=10, height=10)
        from main_pass_gen import gen

        ttk.Separator(master=app, orient=HORIZONTAL, style='blue.TSeparator', class_= ttk.Separator,
        takefocus= 1, cursor='plus').pack(fill=X, pady=2, expand=True)

        generator_button = ttk.Button(app, text="Generator", command=gen)
        add_to_db_button = ttk.Button(app, text="Add to database", command=applytodb)#applytodb #command=lambda: [applytodb(), refresh()]
        add_site_json_button = ttk.Button(app, text="Add suggested site", command=add_suggested)
        settings_button = ttk.Button(app, text="Settings", command=settings)

        generator_button.pack(side=LEFT, anchor=CENTER)
        add_to_db_button.pack(side=LEFT, anchor=CENTER)
        add_site_json_button.pack(side=LEFT, anchor=CENTER)
        settings_button.pack(side=LEFT, anchor=CENTER)

        app.place(x=250, y=315)

    root.mainloop()

#Function to create database Backup 
def settings():
    root = Tk()
    root.title("Settings")

    def edit_main_password():
        my_var=msg.askyesnocancel("Edit?",\
        "Edit" + ' '+ '?', icon='warning',default='no')
        if my_var:
            insert = Tk()
            insert.title("Insert Data")
            insert.resizable(False, False)
            my_conn = get_conn()
            bkg = "#636e72"

            frame = ttk.Frame(insert)
            pass_label = ttk.Label(frame, text="Your new password: ", font=('verdana',12))

            password_label = ttk.Label(frame, text="Password: ", font=('verdana',12))
            password_entry = ttk.Entry(frame, font=('verdana',12))

            password_label_retype = ttk.Label(frame, text="Retype password: ", font=('verdana',12))
            password_entry_retype = ttk.Entry(frame, font=('verdana',12))

            # Funtion to insert a new record
            def editData():
                if password_entry.get() == password_entry_retype.get():
                    if len(password_entry.get()) < 6:
                        pass_label.config(text="Password must be at least 6 characters long.")
                        return
                    hash = hashlib.sha512()
                    hash.update(password_entry.get().encode())
                    hash_hex = hash.hexdigest()

                    insert_query = """UPDATE password SET password = ?;"""
                    vals = (hash_hex,)
                    my_conn.execute(insert_query,vals)
                    my_conn.commit()
                    root.destroy()

                    msg.showinfo(title=None, message="Account edited successfully")
                    insert.destroy()
                else:
                    pass_label.configure(text="Passwords don't match.")

        insert.bind('<Return>', lambda event=None: editData())

        pass_label.grid(row=0, column=1)
        password_label.grid(row=2, column=0, sticky='e')
        password_entry.grid(row=2, column=1, pady=10, padx=10)

        password_label_retype.grid(row=3, column=0, sticky='e')
        password_entry_retype.grid(row=3, column=1, pady=10, padx=10)
        frame.grid(row=0, column=0)
        #my_show()
        insert.mainloop()
        insert.update()


    change_password = ttk.Button(root, text="change password", command=edit_main_password)
    change_password.grid(column=0, row=2)

    spacer = Label(root)
    spacer.grid(column=0, row=3)
    root.mainloop()

def add_suggested():
    def add_to_json():
        root.title("Add Suggested Account")

        # Load the JSON data from the file
        with open("sites_json.json", 'r') as file:
            data = json.load(file)

        # Get the key and new value from the user
        key = "site_name"
        new_value = entry_value.get()

        # Check if the key already exists in the dictionary
        if key in data:
            # If the key exists, append the new value to the existing value
            data[key].append(new_value)
        else:
            # If the key does not exist, create a new key with the new value
            data[key] = [new_value]

        # Save the updated data back to the file
        with open("sites_json.json", 'w') as file:
            json.dump(data, file)
        msg.showinfo(title=None, message="Site " + new_value + " added.")
        root.destroy()

    # Create a Tkinter window with two Entry widgets and a button
    root = tk.Tk()
    label_value = tk.Label(root, text="Add a suggested site:")
    label_value.pack()
    entry_value = tk.Entry(root)
    entry_value.focus()
    entry_value.pack()
    button = ttk.Button(root, text="Add", command=add_to_json)
    button.pack()

    root.mainloop()

main()