from tkinter import *
 
new = Tk()
new.geometry('640x300')
new.title('IoT4Begineers')
 
labelframe = LabelFrame(new, text='LabelFrame Title here')
labelframe.pack()
l = Label(labelframe, text='Label Text')
l.pack()
b= Button(labelframe, text='Button')
b.pack()
mainloop()