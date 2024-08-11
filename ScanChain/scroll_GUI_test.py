import tkinter as tk

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My GUI")

        # Configure the main grid
        self.root.grid_rowconfigure(0, weight=0)  # Title row
        self.root.grid_rowconfigure(1, weight=1)  # Middle frame
        self.root.grid_rowconfigure(2, weight=0)  # Button row

        # Title in the top row with bold and larger font
        self.title_label = tk.Label(self.root, text="My Application Title", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, sticky="nsew")

        # Middle row with a frame containing buttons and scrollbars
        self.middle_frame = tk.Frame(self.root, bg="lightgray")
        self.middle_frame.grid(row=1, column=0, sticky="nsew")

        # Create a canvas for scrollbars
        self.canvas = tk.Canvas(self.middle_frame)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure scrollbars
        self.v_scrollbar = tk.Scrollbar(self.middle_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.middle_frame, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack the canvas and scrollbars
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a window inside the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Populate the scrollable frame with subframes and buttons
        for i in range(10):
            for j in range(10):
                subframe = tk.Frame(self.scrollable_frame, bg="lightblue", padx=2, pady=2)
                subframe.grid(row=i, column=j, padx=2, pady=2)

                button = tk.Button(subframe, text=f"Btn {i},{j}", width=10,
                                   command=lambda i=i, j=j: self.print_coordinates(i, j))
                button.pack(expand=True, fill='both')  # Fill the subframe

        # Update the scroll region
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bind mouse wheel events for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Button in the bottom row
        self.button = tk.Button(self.root, text="Click Me", command=self.on_button_click)
        self.button.grid(row=2, column=0, sticky="nsew")

        # Center the button and title
        self.root.grid_columnconfigure(0, weight=1)

    def print_coordinates(self, i, j):
        print(f"Button coordinates: ({i}, {j})")

    def on_mouse_wheel(self, event):
        # Scroll the canvas when the mouse wheel is used
        self.canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")

    def on_button_click(self):
        print("Button clicked!")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")  # Initial window size
    app = MyApp(root)
    root.mainloop()
