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
from scipy.interpolate import UnivariateSpline
import scipy.signal
import os
import time
import math

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

class GUI:  # Class to write all code in
    def __init__(self):
        self.x_coords = []
        self.y_coords = []

        self.window = tk.Tk()  # Window
        self.window.title("Flourospectroscopy")  # Set title
        self.fullScreen = False  # Variable to track if fullscreen
        self.window.attributes("-fullscreen", self.fullScreen)  # Set fullscreen
        self.window.state('zoomed')

        self.window.geometry(
            f"{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}")  # make window fill entire screen

        frame1top = Frame(self.window)
        frame1 = Frame(self.window)

        # fig = Figure(figsize=(5, 4), dpi=100)
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        # self.line = self.ax.plot(x, y)
        self.ax.plot(self.x_coords, self.y_coords)
        plt.ion()
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
        # frame2tab5 = ttk.Frame(frame2tab)
        frame2tab.add(frame2tab1, text='Moving Average')
        frame2tab.add(frame2tab2, text='Butterworth Filter')
        frame2tab.add(frame2tab3, text='Median Filtering')
        frame2tab.add(frame2tab4, text='Fast Fourier Transform')
        # frame2tab.add(frame2tab5, text='Smoothing Splines')
        # frame2tab.add(frame2tab2, text='Spectral Decomposition')
        # frame2tab.add(frame2tab3, text='Ratiometric Analysis')

        self.moving_average_on = BooleanVar()
        self.moving_average_on.set(True)

        self.low_pass_on = BooleanVar()
        self.low_pass_on.set(True)
        self.high_pass_on = BooleanVar()
        self.high_pass_on.set(False)
        self.band_pass_on = BooleanVar()
        self.band_pass_on.set(False)

        self.median_on = BooleanVar()
        self.median_on.set(True)

        self.fft_on = BooleanVar()
        self.fft_on.set(True)

        # Label(frame2tab1, text="Filters", anchor='w').grid(row=0, column=0, sticky=NSEW)
        self.moving_average = ttk.Checkbutton(frame2tab1, command=self.toggleMovingAverage, text="Moving Average",
                                              variable=self.moving_average_on)
        self.moving_average.grid(row=0, column=0, sticky=NSEW)
        ttk.Label(frame2tab1, text="Window Size:").grid(row=1, column=0, sticky=NSEW)

        self.moving_average_interval = IntVar(value=4)

        self.moving_average_slider = ttk.Scale(frame2tab1, from_=1, to=100, orient=HORIZONTAL, length=450, variable=self.moving_average_interval, command=self.updateMovingAverage)

        self.moving_average_field = ttk.Entry(frame2tab1, textvariable=self.moving_average_interval)
        self.moving_average_field.bind("<Return>", lambda event: self.updateMovingAverage())

        self.moving_average_field.grid(row=2, column=0, sticky=NSEW)
        self.moving_average_slider.grid(row=2, column=1, sticky=NSEW)

        # TODO: Expose Settings for Other Filters
        self.low_pass = ttk.Checkbutton(frame2tab2, command=self.toggleLowPassFiltering, text="Low Pass Filtering", variable=self.low_pass_on)
        self.low_pass.grid(row=0, column=0, sticky=NSEW)
        self.high_pass = ttk.Checkbutton(frame2tab2, command=self.toggleHighPassFiltering, text="High Pass Filtering", variable=self.high_pass_on)
        self.high_pass.grid(row=6, column=0, sticky=NSEW)
        self.band_pass = ttk.Checkbutton(frame2tab2, command=self.toggleBandPassFiltering, text="Band Pass Filtering", variable=self.band_pass_on)
        self.band_pass.grid(row=8, column=0, sticky=NSEW)
        ttk.Label(frame2tab2, text="Order:").grid(row=1, column=0, sticky=NSEW)
        ttk.Label(frame2tab2, text="Cut-off Frequency:").grid(row=3, column=0, sticky=NSEW)

        self.low_pass_order = IntVar(value=3)
        self.low_pass_cut_off = DoubleVar(value=0.05)

        self.lpass_order_slider = ttk.Scale(frame2tab2, from_=1, to=50, orient=HORIZONTAL, length=450, variable=self.low_pass_order, command=self.updateLowPassFiltering)
        self.lpass_order_field = ttk.Entry(frame2tab2, textvariable=self.low_pass_order)
        self.lpass_order_field.bind("<Return>", lambda event: self.updateLowPassFiltering())
        self.lpass_order_field.grid(row=2, column=0, sticky=NSEW)
        self.lpass_order_slider.grid(row=2, column=1, sticky=NSEW)

        self.lpass_freq_slider = ttk.Scale(frame2tab2, from_=0.0000000001, to=0.9999999999, orient=HORIZONTAL, length=450,
                                            variable=self.low_pass_cut_off, command=self.updateLowPassFiltering)
        self.lpass_freq_field = ttk.Entry(frame2tab2, textvariable=self.low_pass_cut_off)
        self.lpass_freq_field.bind("<Return>", lambda event: self.updateLowPassFiltering())
        self.lpass_freq_field.grid(row=4, column=0, sticky=NSEW)
        self.lpass_freq_slider.grid(row=4, column=1, sticky=NSEW)

        self.median = ttk.Checkbutton(frame2tab3, command=self.toggleMedianFiltering, text="Median Filtering", variable=self.median_on)
        self.median.grid(row=0, column=0, sticky=NSEW)

        ttk.Label(frame2tab3, text="Kernel Size:").grid(row=1, column=0, sticky=NSEW)

        self.median_kernel = IntVar(value=7)

        self.median_slider = ttk.Scale(frame2tab3, from_=1, to=100, orient=HORIZONTAL, length=450,
                                               variable=self.median_kernel, command=self.updateMedianFiltering)

        self.median_field = ttk.Entry(frame2tab3, textvariable=self.median_kernel)
        self.median_field.bind("<Return>", lambda event: self.updateMedianFiltering())
        self.median_field.grid(row=2, column=0, sticky=NSEW)
        self.median_slider.grid(row=2, column=1, sticky=NSEW)

        self.fft = ttk.Checkbutton(frame2tab4, command=self.toggleFastFourierTransform, text="Fast Fourier Transform", variable=self.fft_on)
        self.fft.grid(row=0, column=0, sticky=NSEW)
        self.fft_thereshold = DoubleVar(value=1e4)
        self.fft_field = ttk.Entry(frame2tab4, textvariable=self.fft_thereshold)
        self.fft_field.bind("<Return>", lambda event: self.updateFastFourierTransform())
        self.fft_field.grid(row=2, column=0, sticky=NSEW)

        self.moving_averages = []
        self.filteredLowPass = []
        self.filteredHighPass = []
        self.filteredBandPass = []
        self.medianFilteredData = []
        self.fastFourierData = []

        # Label(frame2tab1, text="Save Data", anchor='w').grid(row=4, column=0, sticky=NSEW)

        ttk.Button(frame2tab1, text="Save Moving Average Data",
                   command=lambda: self.saveFile("movingaverage", theycoords=self.moving_averages)).grid(
            row=3, column=0)
        ttk.Button(frame2tab2, text="Save Filtered Low Pass Data",
                   command=lambda: self.saveFile(filename="lowpass", theycoords=self.filteredLowPass)).grid(
            row=5, column=0)
        ttk.Button(frame2tab2, text="Save Filtered High Pass Data",
                   command=lambda: self.saveFile(filename="highpass", theycoords=self.filteredHighPass)).grid(
            row=7, column=0)
        ttk.Button(frame2tab2, text="Save Filtered Band Pass Data",
                   command=lambda: self.saveFile(filename="bandpass", theycoords=self.filteredBandPass)).grid(
            row=9, column=0)
        ttk.Button(frame2tab3, text="Save Median Filtered Data",
                   command=lambda: self.saveFile(filename="medianfiltered", theycoords=self.medianFilteredData)).grid(
            row=3, column=0)
        ttk.Button(frame2tab4, text="Save Fast Fourier Transform Data",
                   command=lambda: self.saveFile(filename="fastfouriertransform", theycoords=self.fastFourierData)).grid(
            row=3, column=0)

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
        ttk.Button(frame1tab3, text="Clear Chart", command=self.clearData).grid(row=0, column=0)

        self.xticks = IntVar(value=5)
        self.yticks = IntVar(value=5)
        self.default_yticks = 5
        self.default_xticks = 5
        plt.minorticks_on()

        # self.yslider = ttk.Scale(frame1tab3, from_=1, to=1000, orient=VERTICAL, command=self.updateValue, variable=self.yticks)
        # self.yslider.set(self.yticks.get())
        # self.yslider.pack()

        # self.xslider = ttk.Scale(frame1tab3, from_=1, to=1000, orient=HORIZONTAL, command=self.updateValue, variable=self.xticks)
        # self.xslider.set(self.xticks)
        # self.xslider.pack()
        ttk.Label(frame1tab3, text="X-axis Ticks: ").grid(row=1, column=0, sticky=NSEW)
        self.xspin = tk.Spinbox(frame1tab3, from_=3, to=100, textvariable=self.xticks, width=10,
                                increment=5, command=self.updateValue)
        self.xslide = ttk.Scale(frame1tab3, from_=3, to=100, orient=HORIZONTAL, length=400, variable=self.xticks,
                  command=self.updateValue)

        self.xspin.grid(row=1, column=1, sticky=NSEW)
        self.xslide.grid(row=1, column=2, sticky=NSEW)
        self.xspin.bind("<Return>", lambda event: self.updateValue())

        ttk.Label(frame1tab3, text="Y-axis Ticks: ").grid(row=2, column=0, sticky=NSEW)
        self.yspin = tk.Spinbox(frame1tab3, from_=3, to=100, textvariable=self.yticks, width=10,
                                increment=5, command=self.updateValue)
        self.yslide = ttk.Scale(frame1tab3, from_=3, to=100, orient=HORIZONTAL, length=400, variable=self.yticks,
                  command=self.updateValue)
        self.yspin.bind("<Return>", lambda event: self.updateValue())

        self.yspin.grid(row=2, column=1, sticky=NSEW)
        self.yslide.grid(row=2, column=2, sticky=NSEW)

        frame1top.place(relx=0, y=0, relwidth=1 / 2, relheight=5 / 8)
        frame1.place(relx=0, rely=5 / 8, relwidth=1 / 2, relheight=3 / 8)
        frame2.place(relx=1 / 2, y=0, relwidth=1 / 2, relheight=1)
        # frame3.place(relx=2/3, y=0, relwidth=1/3, relheight=1)

        self.gridOn = BooleanVar(value=True)
        self.axesOn = BooleanVar(value=True)
        ttk.Checkbutton(frame1tab3, command=self.toggleGrid, text="Grid",
                        variable=self.gridOn).grid(row=3, column=0, sticky=NSEW)
        ttk.Checkbutton(frame1tab3, command=self.toggleAxes, text="Axes",
                        variable=self.axesOn).grid(row=4, column=0, sticky=NSEW)
        #TODO: Hide Data Points (Scatter Plot) and Line

        ttk.Button(frame1tab3, text="Rescale and Relimit", command=self.rescaleAndRelimit).grid(row=5, column=0, sticky=NSEW)
        ttk.Button(frame1tab3, text="Reset x-axis Ticks", command=self.resetXTicks).grid(row=6, column=0, sticky=NSEW)
        ttk.Button(frame1tab3, text="Reset y-axis Ticks", command=self.resetYTicks).grid(row=6, column=1, sticky=NSEW)

        self.updateValue()

        ttk.Button(frame1tab1, text="Select Flourescence Data", command=self.openFile).pack(side=TOP)
        ttk.Button(frame1tab1, text="Select Background Data", command=self.openBackgroundFile).pack(side=TOP)

        # Key Bindings
        self.window.bind("f", self.toggleFullScreen)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        # Status Bar
        # status = Label(self.window, text="By Granwyn Tan. v0.0.1", bd=1, relief=SUNKEN, anchor=SE)
        # status.place(x=0, rely=.98, relwidth=1, relheight=0.02)

        # Main Loop
        self.window.mainloop()

    # Toggles and Settings
    def toggleAxes(self):
        plt.axis(self.axesOn.get())

    def toggleGrid(self):
        plt.grid(self.gridOn.get())

    def rescaleAndRelimit(self):
        self.ax.relim()
        self.ax.autoscale()
        if self.x_coords and self.y_coords:
            self.ax.legend()
        else:
            self.ax.set_ylim(0, 100)
            self.ax.set_xlim(0, 100)
        plt.tight_layout()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def hideDataPoints(self, value):
        self.data_points.set_visible(value)
        self.filterCheck()

    def hideFlourescenceData(self, value):
        self.flourescence_data.set_visible(value)
        self.filterCheck()

    def toggleMovingAverage(self):
        if len(self.ax.lines) > 2:
            self.mvavg.set_visible(self.moving_average_on.get())
        self.filterCheck()

    def toggleLowPassFiltering(self):
        if len(self.ax.lines) > 2:
            self.lpass.set_visible(self.low_pass_on.get())
        self.filterCheck()

    def toggleHighPassFiltering(self):
        if len(self.ax.lines) > 2:
            self.hpass.set_visible(self.high_pass_on.get())
        self.filterCheck()

    def toggleBandPassFiltering(self):
        if len(self.ax.lines) > 2:
            self.bpass.set_visible(self.band_pass_on.get())
        self.filterCheck()

    def toggleMedianFiltering(self):
        if len(self.ax.lines) > 2:
            self.medfilt.set_visible(self.median_on.get())
        self.filterCheck()

    def toggleFastFourierTransform(self):
        if len(self.ax.lines) > 2:
            self.fftline.set_visible(self.fft_on.get())
        self.filterCheck()

    def filterCheck(self):
        if self.x_coords and self.y_coords:
            self.ax.legend()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def updateValue(self, *args):
        self.xticks.set(int(float(self.xspin.get())))
        self.yticks.set(int(float(self.yspin.get())))
        if self.x_coords != [] and self.y_coords != []:
            self.ax.set_xticks(np.arange(min(self.x_coords), max(self.x_coords) + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(min(self.y_coords), max(self.y_coords) + 1, self.yticks.get()))
        else:
            self.ax.set_xticks(np.arange(0, 100 + 1, self.xticks.get()))
            self.ax.set_yticks(np.arange(0, 100 + 1, self.yticks.get()))
        self.rescaleAndRelimit()
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    # Resetting Functions
    def resetXTicks(self):
        self.xticks.set(self.default_xticks)
        self.updateValue()

    def resetYTicks(self):
        self.yticks.set(self.default_yticks)
        self.updateValue()

    # Updating Graphs Functions
    def updateMovingAverage(self, *args):
        # self.moving_average_interval = self.moving_average_interval.get()
        lower_limit = 1
        upper_limit = max(self.x_coords) if self.x_coords and self.y_coords else 100
        if self.moving_average_interval.get() < lower_limit:
            self.moving_average_interval.set(int(lower_limit))
        elif self.moving_average_interval.get() > upper_limit:
            self.moving_average_interval.set(int(upper_limit))
        else:
            self.moving_average_interval.set(self.moving_average_interval.get())

        if self.x_coords and self.y_coords:
            self.moving_averages = self.movingaverage(self.y_coords, self.moving_average_interval.get())
            self.mvavg.set_ydata(self.moving_averages)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def updateLowPassFiltering(self, *args):
        order_minimum = 0
        freq_lower_limit = 0
        freq_upper_limit = 1
        if self.low_pass_cut_off.get() <= freq_lower_limit:
            self.low_pass_cut_off.set(0.0000000001)
        elif self.low_pass_cut_off.get() >= freq_upper_limit:
            self.low_pass_cut_off.set(0.9999999999)
        if self.low_pass_order.get() < order_minimum:
            self.low_pass_order.set(1)
        self.low_pass_order.set(int(self.low_pass_order.get()))
        if self.x_coords and self.y_coords:
            self.filteredLowPass = self.lowPassFiltering(self.y_coords, self.low_pass_order.get(), self.low_pass_cut_off.get())
            self.lpass.set_ydata(self.filteredLowPass)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def updateMedianFiltering(self, *args):
        if self.median_kernel.get() % 1 >= 0.5:
            if int(self.median_kernel.get()) % 2 != 0:
                self.median_kernel.set(math.ceil(self.median_kernel.get()))
            else:
                self.median_kernel.set(math.ceil(self.median_kernel.get())-1)
        else:
            if int(self.median_kernel.get()) % 2 != 0:
                self.median_kernel.set(math.floor(self.median_kernel.get()))
            else:
                self.median_kernel.set(math.floor(self.median_kernel.get())-1)

        if self.x_coords and self.y_coords:
            self.medianFilteredData = self.medianFiltering(self.y_coords, self.median_kernel.get())
            self.medfilt.set_ydata(self.medianFilteredData)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    def updateFastFourierTransform(self, *args):
        self.low_pass_order.set(float(self.low_pass_order.get()))
        if self.x_coords and self.y_coords:
            self.fastFourierData = self.fastFourierTransform(self.y_coords, self.fft_thereshold.get())
            self.fftline.set_ydata(self.fastFourierData)
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

    #TODO: Smoothing Splines

    # Full Screen Toggles
    def toggleFullScreen(self, event):
        self.fullScreen = not self.fullScreen
        self.window.attributes("-fullscreen", self.fullScreen)

    def quitFullScreen(self, event):
        self.fullScreen = False
        self.window.attributes("-fullscreen", self.fullScreen)

    # Main Graph Plotting Function
    def plotGraph(self):
        self.data_points = self.ax.scatter(self.x_coords, self.y_coords, label="Data Points", color="lightcoral")
        self.flourescence_data = self.ax.plot(self.x_coords, self.y_coords, label='Flourescence Data', color="royalblue")
        self.default_xticks = int((max(self.x_coords) - min(self.x_coords)) / 20)
        self.xticks.set(self.default_xticks)
        self.default_yticks = int((max(self.y_coords) - min(self.y_coords)) / 20)
        self.yticks.set(self.default_yticks)
        self.moving_average_slider.config(to=max(self.x_coords))
        self.median_slider.config(to=max(self.x_coords))
        self.moving_averages = self.movingaverage(self.y_coords, self.moving_average_interval.get())
        self.filteredLowPass = self.lowPassFiltering(self.y_coords, self.low_pass_order.get(), self.low_pass_cut_off.get())
        self.filteredHighPass = self.highPassFiltering(self.y_coords)
        self.filteredBandPass = self.bandPassFiltering(self.y_coords)
        self.medianFilteredData = self.medianFiltering(self.y_coords, self.median_kernel.get())
        self.fastFourierData = self.fastFourierTransform(self.y_coords, self.fft_thereshold.get())
        # self.smoothingSplineData = self.smoothingSpline(self.y_coords)
        # print(self.fastFourierData)
        self.mvavg, = self.ax.plot(self.x_coords, self.moving_averages, label="Moving Average")
        self.lpass, = self.ax.plot(self.x_coords, self.filteredLowPass, label="Filtered Low Pass")
        self.hpass, = self.ax.plot(self.x_coords, self.filteredHighPass, label="Filtered High Pass")
        self.bpass, = self.ax.plot(self.x_coords, self.filteredBandPass, label="Filtered Band Pass")
        self.medfilt, = self.ax.plot(self.x_coords, self.medianFilteredData, label="Median Filtered")
        self.fftline, = self.ax.plot(self.x_coords, self.fastFourierData, label="Fast Fourier Transform")
        # self.ssl, = self.ax.plot(self.x_coords, self.smoothingSplineData, label="Smoothing Spline")

        self.fftline.set_visible(self.fft_on.get())
        self.medfilt.set_visible(self.median_on.get())
        self.bpass.set_visible(self.band_pass_on.get())
        self.hpass.set_visible(self.high_pass_on.get())
        self.lpass.set_visible(self.low_pass_on.get())
        self.mvavg.set_visible(self.moving_average_on.get())

        # self.xslider.config(from_=self.xticks.get(), to=(max(self.x_coords) - min(self.x_coords)))
        # self.yslider.config(from_=self.yticks.get(), to=(max(self.y_coords) - min(self.y_coords)))

        self.xslide.config(from_=int(self.xticks.get()), to=int(max(self.x_coords) - min(self.x_coords)))
        self.yslide.config(from_=int(self.yticks.get()), to=int(max(self.y_coords) - min(self.y_coords)))

        # plt.gca()
        self.updateValue()
        # # self.ax.set_xlim(min(self.x_coords)-self.xticks.get(), max(self.x_coords)+self.xticks.get())
        # # self.ax.set_ylim(min(self.y_coords)-self.yticks.get(), max(self.y_coords)+self.yticks.get())

    def clearData(self):
        self.default_yticks = 5
        self.default_xticks = 5
        self.x_coords = []
        self.y_coords = []
        self.moving_averages = []
        self.filteredLowPass = []
        self.filteredHighPass = []
        self.filteredBandPass = []
        self.medianFilteredData = []
        self.fastFourierData = []
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
        self.updateValue()

    # Filters
    def movingaverage(self, interval, window_size=4):
        # np.convolve
        window = np.ones(int(window_size)) / float(window_size)
        return np.convolve(interval, window, 'same')

        # cumsum
        # ret = np.cumsum(interval, dtype=float)
        # ret[window_size:] = ret[window_size:] - ret[:-window_size]
        # return ret[window_size - 1:] / window_size

    def lowPassFiltering(self, data, order=3, cutoff=0.05):
        b, a = scipy.signal.butter(order, cutoff, 'lowpass')
        return scipy.signal.filtfilt(b, a, data)

    def highPassFiltering(self, data):
        b, a = scipy.signal.butter(3, 0.05, 'highpass')
        return scipy.signal.filtfilt(b, a, data)

    def bandPassFiltering(self, data):
        b, a = scipy.signal.butter(3, [.01, .05], 'band')
        return scipy.signal.lfilter(b, a, data)

    def medianFiltering(self, data, kernelsize=7):
        return scipy.signal.medfilt(data, kernel_size=kernelsize)

    def fastFourierTransform(self, signal, threshold=1e4):
        fourier = np.fft.rfft(signal)
        frequencies = np.fft.rfftfreq(len(signal), d=20e-3 / len(signal))
        fourier[frequencies > threshold] = 0
        return np.fft.irfft(fourier)

    # def smoothingSpline(self, data, smoothingFactor=1):
    #     x = self.x_coords
    #     y = self.y_coords
    #     spl = UnivariateSpline(x, y, s=smoothingFactor)
    #     # xs = data
    #     # spl.set_smoothing_factor(smoothingFactor)
    #     return spl(x)

    # Saving File Functionality
    def saveFile(self, filename, theycoords):
        if self.x_coords and self.y_coords:
            try:
                f = filedialog.asksaveasfile(initialfile=f'{filename}.txt', defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
                data = ""
                for i in range(len(self.x_coords)):
                    data += f"{self.x_coords[i]} {theycoords[i]}\n"
                f.write(data)
                f.close()
            except:
                return
        else:
            tk.messagebox.showinfo("Save to File", "No Data Loaded")

    # Opening File Functionality
    def saveFile(self, filename, theycoords):
        if self.x_coords and self.y_coords:
            try:
                f = filedialog.asksaveasfile(initialfile=f'{filename}.txt', defaultextension=".txt",
                                             filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
                data = ""
                for i in range(len(self.x_coords)):
                    data += f"{self.x_coords[i]} {theycoords[i]}\n"
                f.write(data)
                f.close()
            except:
                return
        else:
            tk.messagebox.showinfo("Save to File", "No Data Loaded")

    # Opening File Functionality
    def openBackgroundFile(self):
        # TODO: Background File Functionality and processing
        pass
    def openFile(self):
        filename = filedialog.askopenfilename(initialdir="",
                                              title="Open Acquired Spectral Data File",
                                              filetypes=(("ASCII Files", "*.asc"),
                                                         ("Text Files", "*.txt"),
                                                         ("All Files", "*.*")))
        # Configuring File dialog and varipus file types
        if filename:  # If File Chosen
            # try:
            with open(filename, 'r') as f:  # Open File
                response = tk.messagebox.askquestion("Open Source File",
                                                     f"Open Source File at Filepath: \"{filename}\"?")  # Alert to check if user wants to open file
                if response == "yes":
                    if self.x_coords != [] and self.y_coords != []:
                        self.clearData()
                        self.x_coords = []
                        self.y_coords = []
                    # print(filename)
                    lines = [line.strip() for line in f]
                    for i in range(len(lines)):
                        lines[i] = [float(lines[i].split()[0]), float(lines[i].split()[1])]
                        # print(repr(lines[i]))
                    for x, y in lines:
                        self.x_coords.append(x)
                        self.y_coords.append(y)
                    self.plotGraph()
                    return
                else:
                    return
            return
        # except Exception as e:  # If unable to open file
        #     print(e)
        #     tk.messagebox.showerror("Open Source File",
        #                             f"An unknown error occurred when reading \"{filename}\"")  # Error
        #     return
        else:
            tk.messagebox.showwarning("Open Source File", "No File Opened")  # Warning
            return
    def _quit(self):
        self.window.quit()
        self.window.destroy()
if __name__ == '__main__':
    app = GUI()