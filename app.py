import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os

'''
Notebook syntax: Notebook(master=None, **options)
master: parent window (root).
options: The options accepted by the Notebook() method are height, padding and width. Options are not used in this program.
'''

'''
Frame Syntax: Frame(master=None, **options)
master: tabControl is the parent widget for the tabs.
options: The options accepted by the Frame() method are class_, cursor, padding, relief, style, takefocus, height and width. Options are not used in this program.
'''

class GUI:
    def __init__(self):
        self.window = Tk()
        self.window.title("Flourospectroscopy")
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)
        self.window.geometry(f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}")
        tabControl = ttk.Notebook(self.window)
        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Tab 1')
        tabControl.add(tab2, text='Tab 2')
        tabControl.pack(expand=1, fill="both")
        ttk.Button(tab1, text="Open", command=self.openFile).pack(side=TOP)
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        self.window.mainloop()

    def toggleFullScreen(self, event):
        self.fullScreen = not self.fullScreen
        self.window.attributes("-fullscreen", self.fullScreen)

    def quitFullScreen(self, event):
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)

    def openFile(self):
        self.window.update()
        filename = filedialog.askopenfilename(initialdir="",
                                              title="Open Acquired Spectral Data File",
                                              filetypes=(("ASCII Files", "*.asc"),
                                                         ("Text Files", "*.txt"),
                                                         ("All Files", "*.*")))
        if filename:
            try:
                f = open(filename, 'r')
                if tk.messagebox.askokcancel("Open Source File", f"Open Source File at Filepath: \"{filename}\"?"):
                    print(f.read())
                    f.close()
                    return
                else:
                    return
            except:
                tk.messagebox.showerror("Open Source File", f"Failed to read file at Filepath: \"{filename}\"")
                return
        else:
            tk.messagebox.showwarning("Open Source File", "No File Opened")
            return


if __name__ == '__main__':
    app = GUI()
