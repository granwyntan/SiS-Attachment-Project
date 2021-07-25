import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import numpy as np
from sympy import fft
import timeit
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import scipy.signal
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

class Limiter(ttk.Scale):
    """ ttk.Scale sublass that limits the precision of values. """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        newvalue = int(round(float(newvalue), self.precision))
        self.winfo_toplevel().globalsetvar(self.cget('variable'), (newvalue))
        self.chain(newvalue)

class GUI: # Class to write all code in
    def __init__(self):
        self.x_coords = []
        self.y_coords = []

        self.window = tk.Tk() # Window
        self.window.title("Flourospectroscopy") # Set title
        self.fullScreen = False # Variable to track if fullscreen
        self.window.attributes("-fullscreen", self.fullScreen) # Set fullscreen
        self.window.geometry(f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}") # make window fill entire screen

        frame1top = Frame(self.window)
        frame1 = Frame(self.window)

        # fig = Figure(figsize=(5, 4), dpi=100)
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        # self.line = self.ax.plot(x, y)
        self.ax.plot(self.x_coords, self.y_coords)
        # plt.ion()
        self.ax.grid()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity")
        self.ax.set_title("Raw Data")

        canvas = FigureCanvasTkAgg(self.figure, master=frame1top)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, frame1top)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        frame1tab = ttk.Notebook(frame1)  # tab controller
        # tab1 = ttk.LabelFrame(tabControl, text="FrameName") can use Label Frame and set text if required
        frame1tab1 = ttk.Frame(frame1tab)  # create
        # frame1tab2 = ttk.Frame(frame1tab)
        frame1tab3 = ttk.Frame(frame1tab)
        frame1tab.add(frame1tab1, text='Load Acquired Data')
        # frame1tab.add(frame1tab2, text='Live Acquisition (Anchor)')
        frame1tab.add(frame1tab3, text='Settings')
        frame1tab.pack(expand=1, fill=BOTH)

        frame2 = Frame(self.window)
        frame2tab = ttk.Notebook(frame2)  # tab controller
        frame2tab1 = ttk.Frame(frame2tab)
        frame2tab2 = ttk.Frame(frame2tab)
        frame2tab3 = ttk.Frame(frame2tab)
        frame2tab4 = ttk.Frame(frame2tab)
        frame2tab5 = ttk.Frame(frame2tab)
        frame2tab.add(frame2tab1, text='Moving Average')
        frame2tab.add(frame2tab2, text='Signal Filtering')
        frame2tab.add(frame2tab3, text='Median Filtering')
        frame2tab.add(frame2tab4, text='Fast Fourier Transform')
        frame2tab.add(frame2tab5, text='Smoothing Splines')
        # frame2tab.add(frame2tab2, text='Spectral Decomposition')
        # frame2tab.add(frame2tab3, text='Ratiometric Analysis')

        self.moving_average_on = False
        self.signal_filtering_on = False

        # Label(frame2tab1, text="Filters", anchor='w').grid(row=0, column=0, sticky=NSEW)
        self.moving_average = Checkbutton(frame2tab1, command=self.toggleMovingAverage, text="Moving Average", anchor=W)
        self.setMovingAverage(self.moving_average_on)
        self.moving_average.grid(row=1, column=0, sticky=NSEW)
        self.signal_filtering = Checkbutton(frame2tab1, command=self.toggleSignalFiltering, text="Signal Filtering", anchor=W)
        self.setSignalFiltering(self.signal_filtering_on)
        self.signal_filtering.grid(row=2, column=0, sticky=NSEW)

        self.moving_averages = []
        self.filteredLowPass = []
        self.filteredHighPass = []
        self.filteredBandPass = []

        # Label(frame2tab1, text="Save Data", anchor='w').grid(row=4, column=0, sticky=NSEW)

        ttk.Button(frame2tab1, text="Save Moving Average Data", command=lambda: self.saveFile("movingaverage", theycoords=self.moving_averages)).grid(row=5, column=0, sticky=NSEW)
        ttk.Button(frame2tab2, text="Save Filtered Low Pass",
               command=lambda: self.saveFile(filename="lowpass", theycoords=self.filteredLowPass)).grid(
            row=6, column=0, sticky=NSEW)
        ttk.Button(frame2tab2, text="Save Filtered High Pass Data",
               command=lambda: self.saveFile(filename="highpass", theycoords=self.filteredHighPass)).grid(
            row=6, column=1, sticky=NSEW)
        ttk.Button(frame2tab2, text="Save Filtered Band Pass Data",
               command=lambda: self.saveFile(filename="bandpass", theycoords=self.filteredBandPass)).grid(
            row=6, column=2, sticky=NSEW)

        frame2tab.pack(expand=1, fill=BOTH)

        # frame3 = Frame(self.window)
        # frame3tab = ttk.Notebook(frame3)  # tab controller
        # frame3tab1 = ttk.Frame(frame3tab)  # create
        # frame3tab2 = ttk.Frame(frame3tab)
        # frame3tab.add(frame3tab1, text='Store')
        # frame3tab.add(frame3tab2, text='Train')
        # selected_item = StringVar(self.window)
        # dropdown_options = ["Option 1",
        #                     "Option 2",
        #                     "Option 3"]
        # selected_item.set(dropdown_options[0])
        # dropdown_menu = OptionMenu(frame3tab1, selected_item, *dropdown_options)
        # dropdown_menu.pack()
        #
        # ttk.Radiobutton(frame3tab2, text="Option 1", value=False).pack()
        # ttk.Radiobutton(frame3tab2, text="Option 2", value=True).pack()
        # frame3tab.pack(expand=1, fill=BOTH)

        # Settings
        ttk.Button(frame1tab3, text="Clear Chart", command=self.clearData).grid(row=0, column=0, columnspan=2)

        self.xticks = IntVar(value=5)
        self.yticks = IntVar(value=5)

        # self.yslider = ttk.Scale(frame1tab3, from_=1, to=1000, orient=VERTICAL, command=self.updateValue, variable=self.yticks)
        # self.yslider.set(self.yticks.get())
        # self.yslider.pack()

        # self.xslider = ttk.Scale(frame1tab3, from_=1, to=1000, orient=HORIZONTAL, command=self.updateValue, variable=self.xticks)
        # self.xslider.set(self.xticks)
        # self.xslider.pack()

        self.xspin = tk.Spinbox(frame1tab3, state='readonly', from_=1, to=100, textvariable=self.xticks, width=10, increment=5, command=self.updateValue)
        self.xslide = Limiter(frame1tab3, variable=self.xticks, orient='horizontal', length=200,
                        command=self.updateValue, precision=0)
        self.xslide['to'] = 100
        self.xslide['from'] = 1

        self.xspin.grid(row=1, column=0, sticky='news')
        self.xslide.grid(row=1, column=1, sticky='news')

        self.yspin = tk.Spinbox(frame1tab3, state='readonly', from_=1, to=100, textvariable=self.yticks, width=10, increment=5,command=self.updateValue)
        self.yslide = Limiter(frame1tab3, variable=self.yticks, orient='horizontal', length=200,
                              command=self.updateValue, precision=0)
        self.yslide['to'] = 100
        self.yslide['from'] = 1

        self.yspin.grid(row=2, column=0, sticky='news')
        self.yslide.grid(row=2, column=1, sticky='news')

        frame1top.place(relx=0, y=0, relwidth=1/2, relheight=5/8)
        frame1.place(relx=0, rely=5/8, relwidth=1/2, relheight=3/8)
        frame2.place(relx=1/2, y=0, relwidth=1/2, relheight=1)
        # frame3.place(relx=2/3, y=0, relwidth=1/3, relheight=1)

        self.gridOn = BooleanVar(value=True)
        self.axesOn = StringVar(value='on')
        # TODO: Setting to turn grid on and off
        # TODO: Setting to turn axes and labels on and off
        # plt.grid(False)
        # plt.axis('off')

        self.updateValue(self)

        ttk.Button(frame1tab1, text="Open Files", command=self.openFile).pack(side=TOP)

        # Key Bindings
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        # Status Bar
        # status = Label(self.window, text="By Granwyn Tan. v0.0.1", bd=1, relief=SUNKEN, anchor=SE)
        # status.place(x=0, rely=.98, relwidth=1, relheight=0.02)

        # Main Loop
        self.window.mainloop()

    def toggleMovingAverage(self):
        if self.moving_average_on:
            self.moving_average.config(foreground="red")
            self.moving_average_on = False
        else:
            self.moving_average.config(foreground="green")
            self.moving_average_on = True
        if len(self.ax.lines) > 2:
            self.ax.lines[2].set_visible(self.moving_average_on)
        self.ax.legend()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def setMovingAverage(self, value):
        if not value:
            self.moving_average.config(foreground="red")
        else:
            self.moving_average.config(foreground="green")

    def toggleSignalFiltering(self):
        if self.signal_filtering_on:
            self.signal_filtering.config(foreground="red")
            self.signal_filtering_on = False
        else:
            self.signal_filtering.config(foreground="green")
            self.signal_filtering_on = True
        if len(self.ax.lines) > 2:
            self.ax.lines[5].set_visible(self.signal_filtering_on)
            self.ax.lines[4].set_visible(self.signal_filtering_on)
            self.ax.lines[3].set_visible(self.signal_filtering_on)
        self.ax.legend()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def setSignalFiltering(self, value):
        if not value:
            self.signal_filtering.config(fg="red")
        else:
            self.signal_filtering.config(fg="green")

    def updateValue(self, *args):
        print(self.xspin.get())
        print(self.xslide.get())
        if self.x_coords != [] and self.y_coords != []:
            self.ax.set_xticks(np.arange(min(self.x_coords), max(self.x_coords) + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(min(self.y_coords), max(self.y_coords) + 1, self.yticks.get()))
        else:
            self.ax.set_xticks(np.arange(0, 100 + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(0, 100 + 1, self.yticks.get()))
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    # Full Screen Toggles
    def toggleFullScreen(self, event):
        self.fullScreen = not self.fullScreen
        self.window.attributes("-fullscreen", self.fullScreen)

    def quitFullScreen(self, event):
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)

    # Main Graph Plotting Function
    def plotGraph(self):
        # if self.x_coords and self.y_coords:
        self.ax.scatter(self.x_coords, self.y_coords, label="Data Points", color="lightcoral")
        self.ax.plot(self.x_coords, self.y_coords, label='Line', color="royalblue")
        self.xticks.set((max(self.x_coords) - min(self.x_coords)) / 20)
        self.yticks.set((max(self.y_coords) - min(self.y_coords)) / 20)
        self.moving_averages = self.movingaverage(self.y_coords, 4)
        self.signalFiltering(self.y_coords)
        self.mvavg = self.ax.plot(self.x_coords, self.moving_averages, label="Moving Average")
        self.lp = self.ax.plot(self.x_coords, self.filteredLowPass, label="Filtered Low Pass")
        self.hp = self.ax.plot(self.x_coords, self.filteredHighPass, label="Filtered High Pass")
        self.bp = self.ax.plot(self.x_coords, self.filteredBandPass, label="Filtered Band Pass")
        self.ax.lines[5].set_visible(self.signal_filtering_on)
        self.ax.lines[4].set_visible(self.signal_filtering_on)
        self.ax.lines[3].set_visible(self.signal_filtering_on)
        self.ax.lines[2].set_visible(self.moving_average_on)
        self.median_filtered_data = scipy.signal.medfilt(self.y_coords, kernel_size=7)
        self.ax.plot(self.x_coords, self.median_filtered_data, label="Median Filtered Data")
        # self.xslider.config(from_=self.xticks.get(), to=(max(self.x_coords) - min(self.x_coords)))
        # self.yslider.config(from_=self.yticks.get(), to=(max(self.y_coords) - min(self.y_coords)))

        self.xslide['from'] = int(self.xticks.get())
        self.xslide['to'] = int(max(self.x_coords) - min(self.x_coords))

        self.yslide['from'] = int(self.yticks.get())
        self.yslide['to'] = int(max(self.y_coords) - min(self.y_coords))

        # self.ax.plt.gca()
        self.updateValue(self)
        self.ax.legend()
        self.ax.relim()
        self.ax.autoscale()
        plt.tight_layout()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def clearData(self):
        self.x_coords = self.y_coords = []
        self.ax.clear()
        self.ax.plot(self.x_coords, self.y_coords)
        # self.xslider.config(from_=0, to=100 + 1)
        # self.yslider.config(from_=0, to=100 + 1)
        self.xticks.set(5)
        self.yticks.set(5)
        self.xslide['from'] = 1
        self.xslide['to'] = 100

        self.yslide['from'] = 1
        self.yslide['to'] = 100
        self.xticks.set(5)
        self.yticks.set(5)
        self.ax.grid()
        self.ax.set_xlabel("Wavelength (nm)")
        self.ax.set_ylabel("Intensity")
        self.ax.set_title("Raw Data")
        self.updateValue(self)
        self.ax.relim()
        self.ax.autoscale()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 100)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    # Filters
    def movingaverage(self, interval, window_size):
        # np.convolve
        window = np.ones(int(window_size)) / float(window_size)
        return np.convolve(interval, window, 'same')

        # cumsum
        # ret = np.cumsum(interval, dtype=float)
        # ret[window_size:] = ret[window_size:] - ret[:-window_size]
        # return ret[window_size - 1:] / window_size

    def signalFiltering(self, data):
        b, a = scipy.signal.butter(3, 0.05, 'lowpass')
        self.filteredLowPass = scipy.signal.filtfilt(b, a, data)

        b, a = scipy.signal.butter(3, 0.05, 'highpass')
        self.filteredHighPass = scipy.signal.filtfilt(b, a, data)

        b, a = scipy.signal.butter(3, [.01, .05], 'band')
        self.filteredBandPass = scipy.signal.lfilter(b, a, data)


    def Discrete_Fourier_Transform(x):
        x = np.asarray(x, dtype=float)
        N = x.shape[0]
        n = np.arange(N)
        k = n.reshape((N, 1))
        M = np.exp(-2j * np.pi * k * n / N)
        return np.dot(M, x)
        x = np.random.random(1024)
        np.allclose(Discrete_Fourier_Transform(x), np.fft.fft(x))
        timeit.Discrete_Fourier_Transform(x)
        timeit.np.fft.fft(x)

    def Fast_Fourier_Transform(x):
        """A recursive implementation of the 1D Cooley-Tukey FFT"""
        x = np.asarray(x, dtype=float)
        N = x.shape[0]

        if N % 2 > 0:
            raise ValueError("size of x must be a power of 2")
        elif N <= 32:  # this cutoff should be optimized
            return Discrete_Fourier_Transform(x)
        else:
            X_even = Fast_Fourier_Transform(x[::2])
            X_odd = Fast_Fourier_Transform(x[1::2])
            factor = np.exp(-2j * np.pi * np.arange(N) / N)
            return np.concatenate([X_even + factor[:N / 2] * X_odd,
                                   X_even + factor[N / 2:] * X_odd])
        x = np.random.random(1024)
        np.allclose(Fast_Fourier_Transform(x), np.fft.fft(x))
        timeit.Discrete_Fourier_Transform(x)
        timeit.Fast_Fourier_Transform(x)
        timeit.np.fft.fft(x)

    def FFT_vectorized(x):
        """A vectorized, non-recursive version of the Cooley-Tukey FFT"""
        x = np.asarray(x, dtype=float)
        N = x.shape[0]

        if np.log2(N) % 1 > 0:
            raise ValueError("size of x must be a power of 2")

        # N_min here is equivalent to the stopping condition above,
        # and should be a power of 2
        N_min = min(N, 32)

        # Perform an O[N^2] DFT on all length-N_min sub-problems at once
        n = np.arange(N_min)
        k = n[:, None]
        M = np.exp(-2j * np.pi * n * k / N_min)
        X = np.dot(M, x.reshape((N_min, -1)))

        # build-up each level of the recursive calculation all at once
        while X.shape[0] < N:
            X_even = X[:, :X.shape[1] / 2]
            X_odd = X[:, X.shape[1] / 2:]
            factor = np.exp(-1j * np.pi * np.arange(X.shape[0])
                            / X.shape[0])[:, None]
            X = np.vstack([X_even + factor * X_odd,
                           X_even - factor * X_odd])

        return X.ravel()

    # Saving File Functionality
    def saveFile(self, filename, theycoords):
        if self.x_coords and self.y_coords:
            f = filedialog.asksaveasfile(initialfile=f'{filename}.txt', defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
            data = ""
            for i in range(len(self.x_coords)):
                data += f"{self.x_coords[i]} {theycoords[i]}\n"
            f.write(data)
            f.close()
        else:
            tk.messagebox.showinfo("Save to File", "No Data Loaded")


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
                        if self.x_coords != [] and self.y_coords != []:
                            self.clearData()
                            self.x_coords = []
                            self.y_coords = []
                        print(filename)
                        lines = [line.strip() for line in f]
                        for i in range(len(lines)):
                            lines[i] = [float(lines[i].split()[0]), float(lines[i].split()[1])]
                            print(repr(lines[i]))

                        for x, y in lines:
                            self.x_coords.append(x)
                            self.y_coords.append(y)
                        self.plotGraph()
                        return
                    else:
                        return
            except Exception as e:  # If unable to open file
                print(e)
                tk.messagebox.showerror("Open Source File", f"An unknown error occurred when reading \"{filename}\"")  # Error
                return
        else:
            tk.messagebox.showwarning("Open Source File", "No File Opened")  # Warning
            return


    def _quit(self):
        self.window.quit()
        self.window.destroy()

if __name__ == '__main__':
    app = GUI()
