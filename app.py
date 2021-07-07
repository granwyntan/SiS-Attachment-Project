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
        frame1tab3 = ttk.Frame(frame1tab)
        frame1tab.add(frame1tab1, text='Load Acquired Data')
        frame1tab.add(frame1tab2, text='Live Acquisition (Anchor)')
        frame1tab.add(frame1tab3, text='Settings')
        frame1tab.pack(expand=1, fill=BOTH)

        frame2 = Frame(self.window, width=self.window.winfo_screenwidth() / 3, height=self.window.winfo_screenheight())
        frame2tab = ttk.Notebook(frame2)  # tab controller
        frame2tab1 = ttk.Frame(frame2tab)
        frame2tab2 = ttk.Frame(frame2tab)
        frame2tab3 = ttk.Frame(frame2tab)
        frame2tab.add(frame2tab1, text='Signal Processing')
        frame2tab.add(frame2tab2, text='Spectral Decomposition')
        frame2tab.add(frame2tab3, text='Ratiometric Analysis')

        self.moving_average_on = True
        self.signal_filtering_on = True

        self.moving_average = Checkbutton(frame2tab1, bd=0, command=self.toggleMovingAverage, text="Moving Average")
        self.toggleMovingAverage()
        self.moving_average.grid(row=0, column=0, sticky=NSEW)
        self.signal_filtering = Checkbutton(frame2tab1, bd=0, command=self.toggleSignalFiltering, text="Signal Filtering")
        self.toggleSignalFiltering()
        self.signal_filtering.grid(row=1, column=0, sticky=NSEW)

        frame2tab.pack(expand=1, fill=BOTH)

        frame3 = Frame(self.window, width=self.window.winfo_screenwidth() / 3, height=self.window.winfo_screenheight())
        frame3tab = ttk.Notebook(frame3)  # tab controller
        frame3tab1 = ttk.Frame(frame3tab)  # create
        frame3tab2 = ttk.Frame(frame3tab)
        frame3tab.add(frame3tab1, text='Store')
        frame3tab.add(frame3tab2, text='Train')
        selected_item = StringVar(self.window)
        dropdown_options = ["Option 1",
                            "Option 2",
                            "Option 3"]
        selected_item.set(dropdown_options[0])
        dropdown_menu = OptionMenu(frame3tab1, selected_item, *dropdown_options)
        dropdown_menu.pack()

        frame3tab.pack(expand=1, fill=BOTH)

        self.xticks = IntVar(value=8)
        self.yticks = IntVar(value=5)

        self.yslider = Scale(frame1tab3, from_=1, to=1000, orient=VERTICAL, command=self.updateValue, variable=self.yticks)
        # self.yslider.set(self.yticks.get())
        self.yslider.pack()

        self.xslider = Scale(frame1tab3, from_=1, to=1000, orient=HORIZONTAL, command=self.updateValue, variable=self.xticks)
        # self.xslider.set(self.xticks)
        self.xslider.pack()

        frame1.place(relx=0, y=0, relwidth=1/3, relheight=0.98)
        frame2.place(relx=1/3, y=0, relwidth=1/3, relheight=0.98)
        frame3.place(relx=2/3, y=0, relwidth=1/3, relheight=0.98)

        self.updateValue(self)

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

    def toggleMovingAverage(self):
        if self.moving_average_on:
            self.moving_average.config(fg="red")
            self.moving_average_on = False
        else:
            self.moving_average.config(fg="green")
            self.moving_average_on = True

    def toggleSignalFiltering(self):
        if self.signal_filtering_on:
            self.signal_filtering.config(fg="red")
            self.signal_filtering_on = False
        else:
            self.signal_filtering.config(fg="green")
            self.signal_filtering_on = True

    def updateValue(self, event):
        if self.x_coords and self.y_coords:
            self.ax.set_xticks(np.arange(min(self.x_coords), max(self.x_coords) + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(min(self.y_coords), max(self.y_coords) + 1, self.yticks.get()))
        else:
            self.ax.set_xticks(np.arange(0, 100 + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(0, 100 + 1, self.yticks.get()))
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

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
        self.ax.scatter(self.x_coords, self.y_coords, label="Data Points", color="lightcoral")
        self.ax.plot(self.x_coords, self.y_coords, label='Line', color="royalblue")
        self.xticks.set((max(self.x_coords) - min(self.x_coords)) / 12.5)
        self.yticks.set((max(self.y_coords) - min(self.y_coords)) / 20)
        self.xslider.config(from_=self.xticks.get(), to=(max(self.x_coords) - min(self.x_coords)))
        self.yslider.config(from_=self.yticks.get(), to=(max(self.y_coords) - min(self.y_coords)))
        self.updateValue(self)
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
                        self.x_coords = []
                        self.y_coords = []
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
                tk.messagebox.showerror("Open Source File", f"An unknown error occured when reading \"{filename}\"")  # Error
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
