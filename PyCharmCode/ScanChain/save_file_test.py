import tkinter as tk
from tkinter import filedialog

def save_file():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, 'w') as file:
            file.write("Your content here")

def load_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        print(f"Selected file: {file_path}")

# Create the main window
root = tk.Tk()
root.title("Save File Example")

# Create a button to trigger the save dialog
save_button = tk.Button(root, text="Save As", command=save_file)
save_button.pack(pady=20)

file_button = tk.Button(root, text="Load File", command=load_file)
file_button.pack()

# Run the application
root.mainloop()
