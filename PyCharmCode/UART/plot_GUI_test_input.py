import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import threading
import time



class PlotUpdaterApp:
    def __init__(self, root, port, baudrate=9600):
        self.root = root
        self.root.title("Plot Updater App")

        self.array = np.zeros(512)
        self.current_index = 0
        self.running = True

        # Set up the serial port
        self.ser = serial.Serial(port, baudrate, timeout=1)

        # Create top frame for the checkbox
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.grid(row=0, column=0, sticky='ew')

        # Create bottom frame for the canvas
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.grid(row=1, column=0, sticky='nsew')

        # Create a checkbox to toggle the curve visibility
        self.show_curve = tk.BooleanVar(value=True)
        self.checkbox = ttk.Checkbutton(self.top_frame, text="Show Curve", variable=self.show_curve,
                                        command=self.toggle_curve)
        self.checkbox.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        # Create the matplotlib figure and axes
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot(self.array, 'r-')
        self.ax.set_ylim(0, 1)
        self.ax.set_xlim(0, 512)

        # Create a canvas to display the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.bottom_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.canvas_widget = self.canvas.get_tk_widget()
        self.bottom_frame.bind("<Configure>", self.on_resize)
        self.canvas_widget.config(bg="green")


        # Configure bottom frame grid layout
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Configure root grid layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.update_thread = threading.Thread(target=self.check_for_updates)
        self.update_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_resize(self, event):
        # Adjust the figure size to match the canvas size
        canvas_width = self.canvas_widget.winfo_width()
        canvas_height = self.canvas_widget.winfo_height()
        self.fig.set_size_inches(canvas_width / 100, canvas_height / 100, forward=True)
        # self.canvas.draw()

        # Update the layout
        self.fig.tight_layout()
        self.ax.relim()
        self.ax.autoscale_view()
        # self.canvas_widget.pack(expand=tk.TRUE, fill=tk.BOTH)

        # Draw the updated canvas
        self.canvas.draw()

    def generate_byte_array(self,size):
        # Initialize an empty byte array
        return np.random.rand(size)

    def check_for_updates(self):
        while self.running:
            time.sleep(0.1)
            self.array = self.generate_byte_array(512)
            self.update_plot()

    def toggle_curve(self):
        self.line.set_visible(self.show_curve.get())
        self.canvas.draw()

    def update_plot(self):
        self.line.set_ydata(self.array)
        self.canvas.draw()

    def on_closing(self):
        self.running = False
        self.update_thread.join()
        self.root.quit()


def FPGA_GUI(root):
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    port = 'COM8'  # Replace with your actual serial port
    app = PlotUpdaterApp(root, port)

    FPGA_GUI(root)

    root.destroy()

