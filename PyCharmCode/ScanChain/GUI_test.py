class MyDataObject:
    def __init__(self, value):
        self.value = value
        # Add other attributes as needed

# Create a list of data objects
data_objects = [MyDataObject(i) for i in range(1,5)]

# Now let's create a Tkinter GUI
import tkinter as tk

class DataGUI:
    def __init__(self, root, data_objects):
        self.root = root
        # Create sliders and textboxes
        self.slider = []
        self.textbox = []
        self.low = 0
        self.high = 100

        # Create labels, textboxes, and sliders for each data object
        label = tk.Label(root, text=f"Scanbits value control")
        label.grid(column=2, row=0)
        for i, obj in enumerate(data_objects):
            label = tk.Label(root, text=f"Test Object {i+1}")
            # label.pack(side='left')
            label.grid(column=0, row=i+1)

            # Textbox
            self.textbox.append(tk.Entry(root))
            self.textbox[i].insert(0, str(obj.value))
            # self.textbox[i].pack()
            self.textbox[i].grid(column=2, row=i+1)

            # Slider
            self.slider.append(tk.Scale(root, from_=self.low, to=self.high, orient="horizontal"))
            self.slider[i].set(obj.value)
            # self.slider[i].pack(side='right')
            self.slider[i].grid(column=4, row=i+1)

            # Update values when textbox or slider changes
            self.textbox[i].bind("<FocusOut>", lambda event, index=i: self.update_value(data_objects, event, index, int(self.textbox[index].get())))
            self.slider[i].bind("<ButtonRelease-1>", lambda event, index=i: self.update_value(data_objects, event, index, int(self.slider[index].get())))

        myButton = tk.Button(root, text="Update", command=print_stuff)
        # myButton.pack()
        myButton.grid(column=2, row=len(self.textbox)+1)

        col_count, row_count = root.grid_size()
        for col in range(col_count):
            root.grid_columnconfigure(col, minsize=40)

        for row in range(row_count):
            root.grid_rowconfigure(row, minsize=10)

    def update_value(self, my_list, event, index, value):
        # Update the corresponding data object's values
        try:
            low = self.low
            high = self.high
            if not low <= value <= high:
                value = low if value < low else high
            my_list[index].value = value
            self.slider[index].set(value)
            self.textbox[index].delete(0, "end")
            self.textbox[index].insert(0, str(value))
        except ValueError:
            pass  # Handle invalid input (e.g., non-numeric values)


def print_stuff():
    for objs in data_objects:
        print(f'Val = {objs.value}')


if __name__ == "__main__":
    root = tk.Tk()
    app = DataGUI(root, data_objects)
    root.mainloop()