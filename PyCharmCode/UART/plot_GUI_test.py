import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Matplotlib Plot with Tkinter")

# Create a figure and axis for plotting
fig, ax = plt.subplots()

# Define the data for curves
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Plot initial curves
line1, = ax.plot(x, y1, label='Curve 1')
line2, = ax.plot(x, y2, label='Curve 2')

# Set initial limits
ax.set_xlim(0, 10)
ax.set_ylim(-1.5, 1.5)

# Add legend
ax.legend()

# Create a canvas for the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Function to update the plot based on the checkboxes
def update_plot():
    line1.set_visible(var_curve1.get())
    line2.set_visible(var_curve2.get())
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

# Create checkboxes for toggling curves
var_curve1 = tk.BooleanVar(value=True)
var_curve2 = tk.BooleanVar(value=True)
cb1 = tk.Checkbutton(root, text="Toggle Curve 1", variable=var_curve1, command=update_plot)
cb2 = tk.Checkbutton(root, text="Toggle Curve 2", variable=var_curve2, command=update_plot)
cb1.pack()
cb2.pack()

# Function to update the plot limits based on the sliders
def update_limits_from_sliders(*args):
    xlim = [xlim_slider.get(), xlim_slider2.get()]
    ylim = [ylim_slider.get(), ylim_slider2.get()]
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    canvas.draw()
    # Update textboxes when sliders are changed
    xlim_entry.delete(0, tk.END)
    xlim_entry.insert(0, f"{xlim[0]},{xlim[1]}")
    ylim_entry.delete(0, tk.END)
    ylim_entry.insert(0, f"{ylim[0]},{ylim[1]}")

# Function to update the sliders based on the textboxes
def update_sliders_from_text():
    try:
        xlim = list(map(float, xlim_entry.get().split(',')))
        ylim = list(map(float, ylim_entry.get().split(',')))
        xlim_slider.set(xlim[0])
        xlim_slider2.set(xlim[1])
        ylim_slider.set(ylim[0])
        ylim_slider2.set(ylim[1])
    except:
        pass

# Create frames for x-axis and y-axis controls
xlim_frame = tk.Frame(root)
xlim_frame.pack(pady=5)

ylim_frame = tk.Frame(root)
ylim_frame.pack(pady=5)

# Create sliders and textboxes for x-axis limits
xlim_label = tk.Label(xlim_frame, text="X Limits (min,max):")
xlim_label.grid(row=0, column=0, padx=5)

xlim_entry = tk.Entry(xlim_frame)
xlim_entry.insert(0, "0,10")
xlim_entry.grid(row=0, column=1, padx=5)

xlim_slider = tk.Scale(xlim_frame, from_=0, to=10, orient=tk.HORIZONTAL, label="X Limit Min", command=update_limits_from_sliders)
xlim_slider.set(0)
xlim_slider.grid(row=0, column=2, padx=5)

xlim_slider2 = tk.Scale(xlim_frame, from_=0, to=10, orient=tk.HORIZONTAL, label="X Limit Max", command=update_limits_from_sliders)
xlim_slider2.set(10)
xlim_slider2.grid(row=0, column=3, padx=5)

# Create sliders and textboxes for y-axis limits
ylim_label = tk.Label(ylim_frame, text="Y Limits (min,max):")
ylim_label.grid(row=0, column=0, padx=5)

ylim_entry = tk.Entry(ylim_frame)
ylim_entry.insert(0, "-1.5,1.5")
ylim_entry.grid(row=0, column=1, padx=5)

ylim_slider = tk.Scale(ylim_frame, from_=-2, to=2, orient=tk.HORIZONTAL, label="Y Limit Min", command=update_limits_from_sliders)
ylim_slider.set(-1.5)
ylim_slider.grid(row=0, column=2, padx=5)

ylim_slider2 = tk.Scale(ylim_frame, from_=-2, to=2, orient=tk.HORIZONTAL, label="Y Limit Max", command=update_limits_from_sliders)
ylim_slider2.set(1.5)
ylim_slider2.grid(row=0, column=3, padx=5)

# Bind textboxes to update sliders
xlim_entry.bind("<FocusOut>", lambda e: update_sliders_from_text())
ylim_entry.bind("<FocusOut>", lambda e: update_sliders_from_text())

# Button to apply new limits (optional, if you still want to have it)
apply_button = tk.Button(root, text="Apply Limits", command=lambda: [update_limits_from_sliders(), update_sliders_from_text()])
apply_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
