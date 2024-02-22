"""! @file display.py

Runs a step response test and plots the results. It uses Tkinter, an
old-fashioned and ugly but useful GUI library which is included in Python by default.
This file is based loosely on an example found at
https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
Original program, based on example from above listed source and from reference code
distributed as part of the ME405 curriculum "lab0example.py". 
"""

# Imports
import tkinter
from random import random
import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.backends._backend_tk import (NavigationToolbar2Tk)

# Constants
# CHANGE THIS DEVICE DEPENDING ON SYSTEM TYPE
#__DEV_NAME = "COM6"
__DEV_NAME = "/dev/cu.usbmodem2052339C57522"


def plot_step_data(plot_axes, plot_canvas, xlabel, ylabel, textbox: tkinter.Text):
    """!
    @brief Plot data from a real-world step response test.
    This function reads data from a serial port, then strips lines of strings,
    converting them to floating point numbers. Successfully gathered data is appended
    to arrays of time and encoder count.
    @param plot_axes The set of axes to plot data onto, from Matplotlib
    @param plot_canvas The canvas to plot data onto, from Matplotlib
    @param xlabel The label for the horizontal axis
    @param ylabel The label for the vertical axis
    @param textbox A text box for user input of numeric value
    """

    times = []
    voltages = []   

    ser = serial.Serial(__DEV_NAME, 115200, timeout=2.1) 

    serial_data = textbox.get(1.0, "end-1c")

    print(serial_data)

    try:
        ser.write((serial_data).encode())
        while True:
            line = ser.readline().decode()
            
            line = line.strip('\r\n')

            split_line = line.split(",")

            if len(split_line) > 1:

                times.append(float(split_line[0]))
                voltages.append(float(split_line[1]))

            if not line:
                print("Failed to get data")
                break
    finally:
        print("Closing serial port")
        ser.close()

    # Draw the plot
    plot_axes.plot(times, voltages,marker=".")
    plot_axes.set_xlabel(xlabel)
    plot_axes.set_ylabel(ylabel)
    plot_axes.grid(True)
    plot_canvas.draw()



def tk_matplot(plot_function, xlabel, ylabel, title):
    """!
    @brief Create a TK windows with embedded Matplotlib data.
    This function makes the window, displays it, and runs the user interface
    until the user closes the window. The plot function, which must have been
    supplied by the user, should draw the plot on the supplied plot axes and
    call the draw() function belonging to the plot canvas to show the plot.
    @param plot_function The function passed that plots data
    @param xlabel The label for the horizontal axis
    @param ylabel The label for the vertical axis
    @param title The title for the window opened
    """

    tk_root = tkinter.Tk()
    tk_root.wm_title(title)

    # create a matplotlib figure
    fig = Figure()
    axes = fig.add_subplot()

    # create the drawing canvas and a navigation toolbar
    canvas = FigureCanvasTkAgg(fig, master=tk_root)
    toolbar = NavigationToolbar2Tk(canvas, tk_root, pack_toolbar=False)
    toolbar.update()

    # create the buttons that run tests, clear the screen, and exit the program
    button_quit = tkinter.Button(master=tk_root,
                                 text="Quit",
                                 command=tk_root.destroy)
    button_clear = tkinter.Button(master=tk_root,
                                  text="Clear",
                                  command=lambda: axes.clear() or canvas.draw())
    text_box = tkinter.Text(master=tk_root,
                            width=10,
                            height=1,
                            )
    button_run = tkinter.Button(master=tk_root,
                                text="Run Test",
                                command=lambda: plot_function(axes, canvas, xlabel, ylabel, text_box)
                                )
    
    
    # arrange things in a grid because "pack" is weird
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=4)
    toolbar.grid(row=1, column=0, columnspan=4)
    button_run.grid(row=2, column=0)
    text_box.grid(row=2, column=1)
    button_clear.grid(row=2, column=2)
    button_quit.grid(row=2, column=3)


    # this function runs until the user quits
    tkinter.mainloop()


if __name__ == "__main__":

    tk_matplot(plot_step_data,
               "Time [ms]",
               "Encoder Ticks [#]",
               "Step Response")