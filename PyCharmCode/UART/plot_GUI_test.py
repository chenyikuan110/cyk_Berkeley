import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def update_figure_size(event):
    # Update figure size based on the new dimensions of the canvas
    canvas_width = canvas.get_tk_widget().winfo_width()
    canvas_height = canvas.get_tk_widget().winfo_height()
    fig.set_size_inches(canvas_width / 100, canvas_height / 100, forward=True)
    canvas.draw()

# Create the main Tkinter window
root = tk.Tk()
root.title("Resizable Figure Example")

# Create the canvas frame
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=0, sticky="nsew")

# Create the button frame
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, sticky="ew")

# Create a matplotlib figure and axes
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.plot([0, 1, 2, 3], [0, 1, 4, 9])

# Create a canvas to embed the figure
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.draw()

# Use grid for the canvas widget
canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# Add some buttons to the button frame
button1 = tk.Button(button_frame, text="Button 1")
button1.pack(side=tk.LEFT)
button2 = tk.Button(button_frame, text="Button 2")
button2.pack(side=tk.LEFT)

# Configure row and column weights for the canvas frame
canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(0, weight=1)

# Configure row and column weights for the root window
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)

# Bind the canvas frame resize event to the update function
canvas_frame.bind("<Configure>", update_figure_size)

# Start the Tkinter main loop
root.mainloop()
