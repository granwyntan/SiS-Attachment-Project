import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import os
import time

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
        self.x_coords = []
        self.y_coords = []

        self.window = tk.Tk() # Window
        self.window.title("Flourospectroscopy") # Set title
        self.fullScreen = False # Variable to track if fullscreen
        self.window.attributes("-fullscreen", self.fullScreen) # Set fullscreen
        self.window.geometry(f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}") # make window fill entire screen

        frame1 = Frame(self.window, width=self.window.winfo_screenwidth()/3, height=self.window.winfo_screenheight())

        # fig = Figure(figsize=(5, 4), dpi=100)
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        # self.line = self.ax.plot(x, y)
        self.ax.plot(self.x_coords, self.y_coords, label='Fluorescence')
        # self.ax.ion()
        self.ax.grid()
        self.ax.legend()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity")
        self.ax.set_title("Raw Data")

        canvas = FigureCanvasTkAgg(self.figure, master=frame1)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, frame1)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        canvas.mpl_connect("key_press_event", self.on_key_press)

        frame1tab = ttk.Notebook(frame1)  # tab controller
        # tab1 = ttk.LabelFrame(tabControl, text="FrameName") can use Label Frame and set text if required
        frame1tab1 = ttk.Frame(frame1tab)  # create
        frame1tab2 = ttk.Frame(frame1tab)
        frame1tab.add(frame1tab1, text='Load Acquired Data')
        frame1tab.add(frame1tab2, text='Live Acquisition (Anchor)')
        frame1tab.pack(expand=1, fill=BOTH)

        frame2 = Frame(self.window, width=self.window.winfo_screenwidth() / 3, height=self.window.winfo_screenheight())
        frame2tab = ttk.Notebook(frame2)  # tab controller
        frame2tab1 = ttk.Frame(frame2tab)
        frame2tab2 = ttk.Frame(frame2tab)
        frame2tab3 = ttk.Frame(frame2tab)
        frame2tab.add(frame2tab1, text='Signal Processing')
        frame2tab.add(frame2tab2, text='Spectral Decomposition')
        frame2tab.add(frame2tab3, text='Ratiometric Analysis')
        frame2tab.pack(expand=1, fill=BOTH)

        frame3 = Frame(self.window, width=self.window.winfo_screenwidth() / 3, height=self.window.winfo_screenheight())
        frame3tab = ttk.Notebook(frame3)  # tab controller
        frame3tab1 = ttk.Frame(frame3tab)  # create
        frame3tab2 = ttk.Frame(frame3tab)
        frame3tab.add(frame3tab1, text='Store')
        frame3tab.add(frame3tab2, text='Train')
        frame3tab.pack(expand=1, fill=BOTH)

        frame1.place(relx=0, y=0, relwidth=1/3, relheight=0.98)
        frame2.place(relx=1/3, y=0, relwidth=1/3, relheight=0.98)
        frame3.place(relx=2/3, y=0, relwidth=1/3, relheight=0.98)

        ttk.Button(frame1tab1, text="Open", command=self.openFile).pack(side=TOP)

        # Key Bindings
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        # Status Bar
        status = Label(self.window, text="By Granwyn Tan. v0.0.1", bd=1, relief=SUNKEN, anchor=SE)
        status.place(x=0, rely=.98, relwidth=1, relheight=0.02)

        # Main Loop
        self.window.mainloop()

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, tk.canvas, tk.toolbar)

    # # Graph
    # def Graph(self):

    # Full Screen Toggles
    def toggleFullScreen(self, event):
        self.fullScreen = not self.fullScreen
        self.window.attributes("-fullscreen", self.fullScreen)

    def quitFullScreen(self, event):
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)

    def plotGraph(self):
        self.ax.scatter(self.x_coords, self.y_coords)
        self.ax.plot(self.x_coords, self.y_coords, label='Fluorescence')
        self.ax.set_xticks(np.arange(min(self.x_coords), max(self.x_coords) + 1, 35))
        self.ax.set_yticks(np.arange(min(self.y_coords), max(self.y_coords) + 1, 40))
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    # Opening File Functionality
    def openFile(self):
        filename = filedialog.askopenfilename(initialdir="",
                                              title="Open Acquired Spectral Data File",
                                              filetypes=(("ASCII Files", "*.asc"),
                                                         ("Text Files", "*.txt"),
                                                         ("All Files", "*.*")))
                    # Configuring File dialog and varipus file types
        if filename:  # If File Chosen
            try:
                with open(filename, 'r') as f:  # Open File
                    response = tk.messagebox.askquestion("Open Source File",
                                                         f"Open Source File at Filepath: \"{filename}\"?")  # Alert to check if user wants to open file
                    if response == "yes":
                        print(filename)
                        lines = [line.strip() for line in f]
                        for i in range(len(lines)):
                            lines[i] = [float(lines[i].split()[0]), int(lines[i].split()[1])]
                            print(repr(lines[i]))

                        for x, y in lines:
                            self.x_coords.append(x)
                            self.y_coords.append(y)

                        # TODO: Embed in Tk - https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
                        # TODO: Checkboxes for various filters
                        # TODO: Implement filters
                        self.plotGraph()
                        return
                    else:
                        return
            except Exception as e:  # If unable to open file
                print(e)
                tk.messagebox.showerror("Open Source File", f"Failed to read file at Filepath: \"{filename}\"")  # Error
                return
        else:
            tk.messagebox.showwarning("Open Source File", "No File Opened")  # Warning
            # tk.messagebox.showinfo("Open Source File", "No File Opened")
            return


    def _quit(self):
        self.window.quit()
        self.window.destroy()

if __name__ == '__main__':
    app = GUI()
