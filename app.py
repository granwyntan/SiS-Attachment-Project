import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

class GUI: # Class to write all code in
    def __init__(self):
        self.window = Tk() # Window
        self.window.title("Flourospectroscopy") # Set title
        self.fullScreen = False # Variable to track if fullscreen
        self.window.attributes("-fullscreen", self.fullScreen) # Set fullscreen
        self.window.geometry(f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}") # make window fill entire screen

        tabControl = ttk.Notebook(self.window) # tab controller
        # tab1 = ttk.LabelFrame(tabControl, text="FrameName") can use Label Frame and set text if required
        tab1 = ttk.Frame(tabControl) # create
        tab2 = ttk.Frame(tabControl)
        tabControl.add(tab1, text='Tab 1')
        tabControl.add(tab2, text='Tab 2')
        tabControl.pack(expand=1, fill="both")
        ttk.Button(tab1, text="Open", command=self.openFile).pack(side=TOP)

        # Key Bindings
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        # Status Bar
        status = Label(self.window, text="By Granwyn Tan. v0.0.1", bd=1, relief=SUNKEN, anchor=SE)
        status.pack(fill=X)

        # Main Loop
        self.window.mainloop()

    # # Graph
    # def Graph(self):

    # Full Screen Toggles
    def toggleFullScreen(self, event):
        self.fullScreen = not self.fullScreen
        self.window.attributes("-fullscreen", self.fullScreen)

    def quitFullScreen(self, event):
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)

    # Opening File Functionality
    def openFile(self):
        filename = filedialog.askopenfilename(initialdir="",
                                              title="Open Acquired Spectral Data File",
                                              filetypes=(("ASCII Files", "*.asc"),
                                                         ("Text Files", "*.txt"),
                                                         ("All Files", "*.*")))
                    # Configuring File dialog and varipus file types
        if filename: # If File Chosen
            try:
                with open(filename, 'r') as f: # Open File
                    response = tk.messagebox.askquestion("Open Source File", f"Open Source File at Filepath: \"{filename}\"?") # Alert to check if user wants to open file
                    if response == "yes":
                        print(filename)
                        lines = [line.strip() for line in f]
                        for i in range(len(lines)):
                            lines[i] = [float(lines[i].split()[0]), int(lines[i].split()[1])]
                            print(repr(lines[i]))
                        x_coords = []
                        y_coords = []
                        for x,y in lines:
                            x_coords.append(x)
                            y_coords.append(y)

                        plt.scatter(x_coords, y_coords)
                        plt.plot(x_coords, y_coords, label='Fluorescence')
                        plt.xticks(np.arange(min(x_coords), max(x_coords) + 1, 35))
                        plt.yticks(np.arange(min(y_coords), max(y_coords) + 1, 40))
                        plt.grid()
                        plt.legend()
                        plt.xlabel("Wavelength (nm)")
                        plt.ylabel("Intensity")
                        plt.title("Raw Data")
                        # m, b = np.polyfit(x, y, 1)
                        # plt.plot(x, m * x + b)
                        plt.show()
                        # TODO: Embed in Tk - https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
                        # TODO: Checkboxes for various filters
                        # TODO: Implement filters
                        return
                    else:
                        return
            except Exception as e: # If unable to open file
                print(e)
                tk.messagebox.showerror("Open Source File", f"Failed to read file at Filepath: \"{filename}\"") # Error
                return
        else:
            tk.messagebox.showwarning("Open Source File", "No File Opened") # Warning
            # tk.messagebox.showinfo("Open Source File", "No File Opened")
            return

    def _quit(self):
        self.window.quit()
        self.window.destroy()

if __name__ == '__main__':
    app = GUI()
