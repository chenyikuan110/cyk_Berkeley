import tkinter as tk
from tkinter import ttk

def create_window():
    root = tk.Tk()
    root.title("Button Color Example")

    # Create a style object
    style = ttk.Style()
    style.configure('TButton',
                    background='lightblue',
                    foreground='black')

    # Add a button with the style
    button = ttk.Button(root, text="Click me", style='TButton')
    button.pack(pady=20)

    # Update the style after creating the button
    root.update_idletasks()

    root.mainloop()

create_window()
