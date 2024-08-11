import tkinter as tk

def on_scroll(event):
    if event.delta > 0:
        # Scrolled up
        text.yview_scroll(-1, 'units')
    elif event.delta < 0:
        # Scrolled down
        text.yview_scroll(1, 'units')

def create_scrollable_window():
    global text
    root = tk.Tk()
    root.title("Scroll with Magic Trackpad Example")

    # Create a Text widget with a scrollbar
    text = tk.Text(root, wrap='none', height=20, width=50)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create a vertical scrollbar
    v_scrollbar = tk.Scrollbar(root, orient='vertical', command=text.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the Text widget to use the scrollbar
    text.config(yscrollcommand=v_scrollbar.set)

    # Add some content to the Text widget
    for i in range(100):
        text.insert(tk.END, f"Line {i+1}\n")

    # Bind the MouseWheel event to the scroll handler
    root.bind_all("<MouseWheel>", on_scroll)

    root.mainloop()

create_scrollable_window()
