from tkinter import *
from tkinter import filedialog

def openFile():
    filepath = filedialog.askopenfilename(initialdir="C:\\Users\\Cakow\\PycharmProjects\\Main",
                                          title="Open Acquired Spectral Data File",
                                          filetypes= (("Text Files","*.txt"), ("ASCII Files","*.asc"),
                                          ("All Files","*.*")))
    file = open(filepath,'r')
    print(file.read())
    file.close()

window = Tk()
button = Button(text="Open", command=openFile)
button.pack()
window.mainloop()