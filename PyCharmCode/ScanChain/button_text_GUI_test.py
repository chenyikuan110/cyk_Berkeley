import tkinter as tk

# Create the main window
root = tk.Tk()
root.geometry("200x100")

# Create a button
my_button = tk.Button(root, text="Click Me")
my_button.pack(pady=20)

# Get the text of the button
button_text = my_button.cget('text')
# Alternatively, you can use: button_text = my_button['text']

# Print the button text
print("Button text:", button_text)

# Run the application
root.mainloop()
