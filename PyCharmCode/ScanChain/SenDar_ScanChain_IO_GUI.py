# Created by Yikuan Chen
# serial write part modified from code provided by Rami Hijab
import copy
import os
import textwrap
import serial
import time
import numpy as np
import csv
import tkinter as tk  # GUI
from tkinter import ttk, StringVar
from tkinter import filedialog
from ttkthemes import ThemedStyle
from tkmacosx import Button as macButton
import os
import subprocess


# screen info
h_size = 900
w_size = 1500

# Environment var
# VM_freq 16368 good
print_info = True
Emulating = True
port = 'COM5' if os.name == 'nt' else '/dev/ttys002' # COM9 for arduino uno, COM5 for arduino due, COM2<->4 are virtual
baudrate = 9600
scanchain_size = 648
scan_data_size = 597

# Arduino Command (Serial)
CMD_WRITE = b'ascwrite\n'
CMD_LOAD = b'ascload\n'
CMD_READ = b'ascread\n'
MSG_WRITE = 'Executing ASC Write'
MSG_WRITE_ERROR = 'Error in the ASC Write'
MSG_WRITE_COMPLETE = 'ASC Write Complete'
MSG_LOAD = 'Executing ASC Load'

TX_combinedcode = False
combinecode_text = f'combinedcode_' if TX_combinedcode else ''
csv_name = f'config/Full_Scan_bits_newTX_{combinecode_text}unfolded.csv'

def is_dark_mode():
    try:
        # Run the AppleScript to check the appearance mode
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get dark mode of appearance preferences'],
            capture_output=True,
            text=True
        )
        # Parse the result
        return result.stdout.strip() == 'true'
    except Exception as e:
        print(f"Error: {e}")
        return False

sys_darkmode = is_dark_mode()

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


config_FULL = {
    'scan_address': 647,
    'domain': 'FULL',
    'channels': 1,
    'chain size': 647,
    'chain direction': 'in'
}

config = config_FULL
curr_msb = 0


class ScanBit:
    def __init__(self, domain, signal_name, bit_width, bits, off_bits=0, msb_first=True, comment=''):
        """
        Custom type representing a scan bit.

        Args:
            signal_name (str): Name of the signal.
            bit_width (int): Width of the bit field.
            lsb_index (int): Index of the least significant bit (LSB).
            bits (int): Actual value of the bit field.
        """
        global config
        self.domain = domain
        self.msb_first = msb_first
        self.signal_name = signal_name
        self.bit_width = bit_width
        global curr_msb
        self.lsb_index = curr_msb - bit_width + 1
        self.value = bits
        self.default_val = bits  # one-time set
        self.off_bits = off_bits  # some bits are active low
        self.bits_string = '{:0{width}b}'.format(bits, width=bit_width)
        self.off_bits_string = '{:0{width}b}'.format(off_bits, width=bit_width)
        self.comment = comment
        curr_msb -= bit_width

    def set_val(self, val):
        self.value = val
        bits_string = '{:0{width}b}'.format(val, width=self.bit_width)
        self.bits_string = bits_string  # if self.msb_first else bits_string[::-1]

    def get_val(self):
        return self.value

    def get_def_val(self):
        return self.default_val

    def set_off_val(self, off_val):
        self.off_bits = off_val
        self.off_bits_string = '{:0{width}b}'.format(off_val, width=self.bit_width)


# GUI tool
class DataGUI:
    def __init__(self, root, csv_path_name, my_ser, scan_count, my_SCAN_LIST):
        self.root = root

        self.csv_path = csv_path_name
        self.csv_saved = True
        self.csv_path_string = StringVar()
        self.csv_path_string.set(f'CSV: {self.csv_path} [Saved]')
        self.slider = []
        self.textbox = []
        self.signal_name = []
        self.DCOC_buttons = []

        my_style = ttk.Style()
        my_style.configure('dark.TFrame', background='#3A3845')  # dark
        my_style.configure('pink.TFrame', background='#F7CCAC')  # pink
        my_style.configure('yellow.TFrame', background='#FFE93D')  # yellow
        my_style.configure('blue.TFrame', background='#0D06FF')  # blue
        my_style.configure('red.TFrame', background='#FF0000')  # red

        # self.root.configure(bg='white')
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)

        tkButton = tk.Button if os.name == 'nt' else macButton


        # title
        self.label = tk.Label(self.root, text=f"SenDar Scanbits Control Dashboard v1.0", font=("Arial", 15, "bold"))
        self.label.grid(column=0, row=0, sticky="ew")

        # Create labels, textboxes, and sliders for each data object
        num_rows = 40

        # Middle row with a frame containing buttons and scrollbars
        self.scanTableFrame = tk.Frame(self.root)
        # self.scanTableFrame.configure(bg='white')
        self.scanTableFrame.grid(row=1, column=0, sticky="nsew")

        # Create a canvas for scrollbars
        self.canvas = tk.Canvas(self.scanTableFrame)
        # self.canvas.configure(bg='white')
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.scanTableFrame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.scanTableFrame, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack the canvas and scrollbars
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a window inside the canvas
        # self.scrollable_frame.configure(bg='white')
        scanTableFrame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        row_pos = 0
        col_pos = 0
        prev_prefix = ''
        max_word_cnt = 20
        self.scanBitFrame = []
        self.reset_buttons = []
        self.off_buttons = []
        self.csv_path_label = None

        curr_domain_begin = 0
        curr_domain_end = 0
        for i, obj in enumerate(my_SCAN_LIST):
            self.signal_name.append(obj.signal_name)
            if max_word_cnt < len(obj.signal_name):
                max_word_cnt = len(obj.signal_name)
            curr_prefix = obj.signal_name.split('_')

            # row_pos = int(i % num_rows)
            # col_pos = int(i / num_rows)
            # if row_pos+col_pos != 0:
            if prev_prefix != curr_prefix[0] and curr_prefix[0] != 'IREF' and prev_prefix != 'IREF':
                # update the size of the previous col
                curr_domain_end = i
                self.scrollable_frame.grid_columnconfigure(col_pos, minsize=40)

                # resize the labels in the finished col
                for j in range(curr_domain_begin, curr_domain_end):
                    self.scanBitFrame[j].grid_columnconfigure(0, minsize=max_word_cnt * 7 + 20)
                curr_domain_begin = i
                max_word_cnt = 0

                # set title for new col
                scanBitTitleFrame = tk.Frame(self.scrollable_frame, width=40, height=15)
                scanBitTitleFrame.grid(column=col_pos + 1, row=0 + 1)
                label = tk.Label(scanBitTitleFrame, text=f"{curr_prefix[0]} Config")
                scanBitTitleFrame.grid_columnconfigure(0, minsize=20)
                label.grid(column=0, row=0, sticky="se")

                # set a reset and all off for this col
                scanGroupButtonFrame = tk.Frame(self.scrollable_frame, width=40, height=15)
                scanGroupButtonFrame.grid(column=col_pos + 1, row=0 + 1)
                scanGroupButtonFrame.grid_columnconfigure(0, minsize=20)

                domain = curr_prefix[0]
                self.reset_buttons.append(tkButton(scanGroupButtonFrame, text=f"reset {domain}",
                                                    command=lambda name=domain: self.update_group(my_ser, my_scan_count,
                                                                                                  my_SCAN_LIST, name,
                                                                                                  'on')))
                self.reset_buttons[-1].grid(column=0, row=0, padx=10)
                self.off_buttons.append(tkButton(scanGroupButtonFrame, text=f"turnoff {domain}",
                                                  command=lambda name=domain: self.update_group(my_ser, my_scan_count,
                                                                                                my_SCAN_LIST, name,
                                                                                                'off')))
                self.off_buttons[-1].grid(column=1, row=0)
                if domain == 'TX' or domain == 'VM':
                    onoff_val = 0
                    # found_object = next((obj for obj in my_SCAN_LIST if obj.signal_name[0:10] == f'{domain}_DCOC_SP'),
                    #                     None)
                    # if found_object:
                    if any((obj.signal_name[0:9] == f'{domain}_DCOC_S' and obj.value == 1) for obj in my_SCAN_LIST):
                        onoff_val = onoff_val + 1 # if obj.value == 1 else onoff_val

                    # found_object = next(
                    #         (obj for obj in my_SCAN_LIST if obj.signal_name[0:10] == f'{domain}_DCOC_SN'),
                    #         None)
                    # if found_object:
                    #     onoff_val = onoff_val + 1 if obj.value == 1 else onoff_val

                    onoff = 'on' if onoff_val > 0 else 'off'
                    fg = 'black' if onoff_val > 0 else 'white'  # text color
                    self.DCOC_buttons.append(
                        tkButton(scanGroupButtonFrame, text=f"{domain} DCOC {onoff}", bg="red", fg=fg,
                                  command=lambda name=domain: self.DCOC_toggle(my_ser, my_scan_count,
                                                                               my_SCAN_LIST, name)))
                    self.DCOC_buttons[-1].grid(column=2, row=0, padx=10)

                # update col and row pos
                row_pos = 2
                col_pos += 1
            prev_prefix = curr_prefix[0]

            self.scanBitFrame.append(tk.Frame(self.scrollable_frame, width=40, height=15))
            self.scanBitFrame[i].grid(column=col_pos, row=row_pos + 1, padx=0)

            # Label
            label = tk.Label(self.scanBitFrame[i], text=f"{obj.signal_name}")
            # label.pack(side='left')
            # self.scanBitFrame[i].grid_columnconfigure(0, minsize=20)
            label.grid(column=0, row=0, sticky="se")

            # Textbox
            textEntryFrame = tk.Frame(self.scanBitFrame[i], width=70, height=20)
            textEntryFrame.grid(row=0, column=1, sticky="se")
            textEntryFrame.columnconfigure(0, weight=10)  # allow the column inside the entryFrame to grow
            textEntryFrame.grid_propagate(False)

            self.textbox.append(tk.Entry(textEntryFrame, fg='black', bg='orange' if obj.msb_first == False else 'white'))
            display_val = str(obj.value) if obj.msb_first else str(self.bit_reverse(obj.value, obj.bit_width))
            self.textbox[i].insert(0, display_val)
            self.textbox[i].grid(sticky="se")
            # Update values when textbox or slider changes
            self.textbox[i].bind("<FocusOut>", lambda event, index=i: self.update_value(
                my_SCAN_LIST, self.signal_name[index], event, index, int(self.textbox[index].get())))

            # Slider
            low = 0
            high = 2 ** obj.bit_width - 1
            self.slider.append(tk.Scale(self.scanBitFrame[i], from_=low, to=high, orient="horizontal"))
            display_val = str(obj.value) if obj.msb_first else str(self.bit_reverse(obj.value, obj.bit_width))
            self.slider[i].set(display_val)
            # self.slider[i].pack(side='right')

            # if high > 1:
            self.slider[i].grid(column=2, row=0, sticky="se")
            self.slider[i].bind("<ButtonRelease-1>", lambda event, index=i: self.update_value(
                my_SCAN_LIST, self.signal_name[index], event, index, int(self.slider[index].get())))
            row_pos += 1

        # Resize the label width of the last col
        for j in range(curr_domain_begin, len(my_SCAN_LIST)):
            self.scanBitFrame[j].grid_columnconfigure(0, minsize=max_word_cnt * 7)

        # Update the scroll region
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bind mouse wheel events for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # buttons
        controlFrame = ttk.Frame(root)
        controlFrame.grid(column=0, row=2, pady=10)
        self.root.grid_columnconfigure(0, weight=1)

        num_vars = len(my_SCAN_LIST)
        center_col = int(num_vars / num_rows / 2)

        write_button = tkButton(controlFrame, text="Write Scan Chain",
                                 command=lambda: scan_write_and_read(my_ser, scan_count, my_SCAN_LIST))
        write_button.grid(column=center_col, row=num_rows + 1)
        controlFrame.columnconfigure(center_col, minsize=250)

        allreset_button = tkButton(controlFrame, text="Reset Scan Chain",
                                    command=lambda: self.reset_all(my_ser, my_scan_count, my_SCAN_LIST))
        allreset_button.grid(column=center_col - 1, row=num_rows + 1)

        alloff_button = tkButton(controlFrame, text="Turn off All",
                                  command=lambda: self.turnoff_all(my_ser, scan_count, my_SCAN_LIST))
        alloff_button.grid(column=center_col + 1, row=num_rows + 1)

        # save load buttons
        dataIOFrame = ttk.Frame(root)
        dataIOFrame.grid(column=0, row=3, pady=10)
        save_button = tkButton(dataIOFrame, text="Save Config",
                                command=lambda: self.save_file(my_SCAN_LIST))
        save_button.grid(column=center_col - 1, row=num_rows + 1, padx=10)

        load_button = tkButton(dataIOFrame, text="Load Config",
                                command=lambda: self.load_file(my_ser, my_SCAN_LIST))
        load_button.grid(column=center_col + 1, row=num_rows + 1, padx=10)

        # path display
        self.csv_path_label = tk.Label(root, textvariable=self.csv_path_string, bg='#7FFF00')
        # label.pack(side='left')
        # self.scanBitFrame[i].grid_columnconfigure(0, minsize=20)
        self.csv_path_label.grid(column=0, row=4, sticky="nswe")

        root.update_idletasks()

    def on_mouse_wheel(self, event):
        # Scroll the canvas when the mouse wheel is used
        if os.name == 'nt':
            self.canvas.yview_scroll(int(-1 * (event.delta // 120)), "units")
        else:
                if event.delta > 0:
                    # Scrolled up
                    self.canvas.yview_scroll(-1, 'units')
                elif event.delta < 0:
                    # Scrolled down
                    self.canvas.yview_scroll(1, 'units')

    def update_value(self, my_SCAN_LIST, signal_name, event, index, value):
        # Update the corresponding data object's values
        try:
            for scans in my_SCAN_LIST:
                if signal_name == scans.signal_name:
                    low = 0
                    high = 2 ** scans.bit_width - 1
                    if not low <= value <= high:
                        value = low if value < low else high
                    value = value if scans.msb_first else self.bit_reverse(value, scans.bit_width)
                    modify_val(my_SCAN_LIST, signal_name, value)
                    display_val = str(scans.value) if scans.msb_first else str(
                        self.bit_reverse(scans.value, scans.bit_width))
                    self.slider[index].set(display_val)
                    self.textbox[index].delete(0, "end")
                    self.textbox[index].insert(0, display_val)
                    break
            self.csv_saved = False
            self.csv_path_string.set(f'CSV: {self.csv_path} [Unsaved]')
            self.csv_path_label.config(bg='red')
        except ValueError:
            pass  # Handle invalid input (e.g., non-numeric values)

    def update_group_slider_n_textbox(self, group_name, change_all=False):
        for i, signal_name in enumerate(self.signal_name):
            display_val = str(my_SCAN_LIST[i].get_val()) if my_SCAN_LIST[i].msb_first else str(
                self.bit_reverse(my_SCAN_LIST[i].get_val(), my_SCAN_LIST[i].bit_width))
            if change_all:
                self.slider[i].set(display_val)
                self.textbox[i].delete(0, "end")
                self.textbox[i].insert(0, display_val)
            else:
                if signal_name[0:2] == group_name:
                    self.slider[i].set(display_val)
                    self.textbox[i].delete(0, "end")
                    self.textbox[i].insert(0, display_val)
        self.csv_saved = False
        self.csv_path_string.set(f'CSV: {self.csv_path} [Unsaved]')
        self.csv_path_label.config(bg='red')

    def update_group(self, my_ser, my_scan_count, my_SCAN_LIST, group_name, op):
        try:
            group_op(my_ser, my_scan_count, my_SCAN_LIST, group_name, op)

            # update the sliders and text boxes
            self.update_group_slider_n_textbox(group_name, change_all=False)

            # update toggle buttons
            if group_name == 'TX' or group_name == 'VM':
                if any((obj.signal_name[0:9] == f'{group_name}_DCOC_S' and obj.value == 1) for obj in my_SCAN_LIST):
                    self.update_DCOC_buttons(group_name, new_state=1)
                else:
                    self.update_DCOC_buttons(group_name, new_state=0)
            self.csv_saved = False
            self.csv_path_string.set(f'CSV: {self.csv_path} [Unsaved]')
            self.csv_path_label.config(bg='red')
        except ValueError:
            pass  # Handle invalid input (e.g., non-numeric values)

    def update_DCOC_buttons(self, name, new_state):
        for DCOC_button in self.DCOC_buttons:
            text = DCOC_button.cget('text')
            if text[0:2] == name:
                onoff = 'on' if new_state == 1 else 'off'
                bg = '#7FFF00' if new_state == 1 else 'red'  # button color
                if not sys_darkmode:
                    fg = 'black' if new_state == 1 else 'white'  # text color
                else:
                    fg = 'black' if new_state == 1 else 'black'  # text color
                DCOC_button.config(text=f'{name} DCOC {onoff}', bg=bg, fg=fg)

    def DCOC_toggle(self, my_ser, my_scan_count, my_SCAN_LIST, group_name):
        try:
            new_state = -1
            for scans in my_SCAN_LIST:
                cmd_name = scans.signal_name
                if cmd_name[0:10] == f'{group_name}_DCOC_SP':
                    new_state = 1 if scans.value == 0 else 0
                    modify_val(my_SCAN_LIST, cmd_name, new_state)
                if cmd_name[0:10] == f'{group_name}_DCOC_SN':
                    modify_val(my_SCAN_LIST, cmd_name, scans.off_bits)
                elif cmd_name[0:13] == f'{group_name}_DCOC_CTRL_':
                    if scans.bit_width > 1:
                        if scans.default_val == 0:
                            modify_val(my_SCAN_LIST, cmd_name, 32 if new_state == 1 else scans.off_bits)
                        else:
                            modify_val(my_SCAN_LIST, cmd_name, scans.default_val if new_state == 1 else scans.off_bits)
                    else:
                        modify_val(my_SCAN_LIST, cmd_name, 0)
            scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)

            # update the sliders and text boxes
            self.update_group_slider_n_textbox(group_name, change_all=False)

            # update buttons
            self.update_DCOC_buttons(group_name, new_state)
            self.csv_saved = False
            self.csv_path_string.set(f'CSV: {self.csv_path} [Unsaved]')
            self.csv_path_label.config(bg='red')

        except ValueError:
            pass  # Handle

    def reset_all(self, my_ser, my_scan_count, my_SCAN_LIST):
        try:
            for scans in my_SCAN_LIST:
                cmd_name = scans.signal_name
                modify_val(my_SCAN_LIST, cmd_name, scans.default_val)
            scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)

            # update the sliders and text boxes
            self.update_group_slider_n_textbox('', change_all=True)
            # update toggle buttons
            for name in ['TX', 'VM']:
                if any((obj.signal_name[0:9] == f'{name}_DCOC_S' and obj.value == 1) for obj in my_SCAN_LIST):
                    self.update_DCOC_buttons(name, new_state=1)
                else:
                    self.update_DCOC_buttons(name, new_state=0)
            self.csv_saved = False
            self.csv_path_string.set(f'CSV: {self.csv_path} [Saved]')
            self.csv_path_label.config(bg='#7FFF00')

        except ValueError:
            pass  # Handle invalid input (e.g., non-numeric values)

    def turnoff_all(self, my_ser, my_scan_count, my_SCAN_LIST):
        try:
            for scans in my_SCAN_LIST:
                cmd_name = scans.signal_name
                modify_val(my_SCAN_LIST, cmd_name, scans.off_bits)
            scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)

            # update the sliders and text boxes
            self.update_group_slider_n_textbox('', change_all=True)

            # update toggle buttons
            for name in ['TX', 'VM']:
                self.update_DCOC_buttons(name, new_state=0)
            self.csv_saved = False
            self.csv_path_string.set(f'CSV: {self.csv_path} [Unsaved]')
            self.csv_path_label.config(bg='red')

        except ValueError:
            pass  # Handle invalid input (e.g., non-numeric values)

    def unfold_bits_save_file(self, name, width, msb_first, bits):
        bit_list = []
        for i in range(width):
            bit_list.append([name + '[' + str(((width - i - 1) if msb_first else i)) + ']', bits[i]])
        return bit_list

    def save_file(self, my_SCAN_LIST):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Text files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            print(f"Saving config to file: {file_path}")
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',')
                csv_writer.writerow(['Scan_Index',
                                     'Domain',
                                     'Bit_Name',
                                     'Bit',
                                     'Off_Bit',
                                     'Comment'])
                curr_index = scan_data_size - 1
                for scan in my_SCAN_LIST:
                    unfolded_list = self.unfold_bits_save_file(scan.signal_name, scan.bit_width, scan.msb_first,
                                                               scan.bits_string)
                    off_bit_list = self.unfold_bits_save_file(scan.signal_name, scan.bit_width, scan.msb_first,
                                                              scan.off_bits_string)
                    scan.default_val = scan.value
                    for i, row in enumerate(list(unfolded_list)):
                        csv_writer.writerow([curr_index, scan.domain, row[0], row[1], off_bit_list[i][1], scan.comment])
                        curr_index -= 1
            self.csv_path = file_path
            self.csv_saved = True
            self.csv_path_string.set(f'CSV: {self.csv_path} [Saved]')
            self.csv_path_label.config(bg='#7FFF00')

    def load_file(self, my_ser, my_SCAN_LIST):
        file_path = filedialog.askopenfilename()
        if file_path:
            print(f"Loading file: {file_path}")
            scan_count, temp_SCAN_LIST = scan_init(file_path)
            for i in range(len(my_SCAN_LIST)):
                my_SCAN_LIST[i] = copy.deepcopy(temp_SCAN_LIST[i])
            self.reset_all(my_ser, scan_count, my_SCAN_LIST)
            self.csv_path = file_path
            self.csv_saved = True
            self.csv_path_string.set(f'CSV: {self.csv_path} [Saved]')
            self.csv_path_label.config(bg='#7FFF00')


    def bit_reverse(self, value, bitwidth):
        # Convert the decimal number to binary and reverse the bits
        binary_str = format(value, '0' + str(bitwidth) + 'b')
        reversed_binary_str = binary_str[::-1]

        # Convert the reversed binary back to decimal
        reversed_decimal = int(reversed_binary_str, 2)
        return reversed_decimal


def print_msg(msg):
    if 'Error' in msg:
        print(bcolors.WARNING + msg + bcolors.ENDC)
    else:
        print(bcolors.OKGREEN + msg + bcolors.ENDC)


def error_msg(msg):
    print(bcolors.WARNING + msg + bcolors.ENDC)


# Read the entire serial buffer (msg from Arduino)
def read_buffer(s):
    # tdata = s.read() # set a blocking read
    time.sleep(0.05)
    size = s.in_waiting
    msg = s.read(size)
    # msg = tdata+msg
    print('>> reading ' + str(len(msg.decode('utf-8').rstrip('\r\n'))) + " bytes from Serial buffer...")
    return msg.decode('utf-8').rstrip('\r\n')


def unfold_bits_scan_write(width, bits):
    bit_list = []
    for i in range(width):
        bit_list.append(int(bits[i]))
    return bit_list


# turn csv into ScanBit data struct
def csv_to_ScanBit(reader_obj):
    scan_count = 0
    # scan_buffer = []
    SCAN_LIST = []
    var_name = ''
    domain = ''
    bits = []
    off_bits = []
    count = 0

    # Send string to uC and program into IC
    print("Starting Write to Scan Buffer...")

    curr_bit_index = 0
    recorded_bit_index = 0
    for row in list(reader_obj):
        msb_first = True
        temp = row[2].split('[')

        if temp[0] == 'Bit_Name':
            continue  # skipping the header row

        curr_bit_index = int(temp[1].split(']')[0])
        if var_name != temp[0]:  # new var name
            if bits != []:  # wrap up the previous loaded bit group
                if recorded_bit_index > 0:
                    msb_first = False
                val = 0
                off_val = 0
                # print(var_name, bits, count)
                for i in range(count):
                    # print(i, bits[i], 2**(count-i-1))
                    val += bits[i] * (2 ** (count - i - 1))
                    off_val += off_bits[i] * (2 ** (count - i - 1))
                # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
                # SCAN_LIST.append(ScanBit('DCOC_SN_QE', 1, 0b0))
                SCAN_LIST.append(ScanBit(domain, var_name, count, int(val), off_bits=int(off_val), msb_first=msb_first))
                if print_info:
                    print(
                        f'Wrote to buffer \'{var_name: >35}[{count - recorded_bit_index - 1}:{recorded_bit_index}]\' with 0b{val:>0{count}b},'
                        f' Unsigned Decimal Val = {val},'
                        f' Off value Decimal = {off_val}, '
                        f' msb_first={1 if msb_first else 0}.')

            var_name = temp[0]  # get the name of the new bit group
            domain = row[1]
            count = 0
            bits = []
            off_bits = []

        recorded_bit_index = curr_bit_index
        # append the new bit
        bits.append(int(row[3]))
        off_bits.append(int(row[4]))
        scan_count += 1
        count += 1

    # wrap up the last one
    msb_first = True
    if bits != []:
        if recorded_bit_index > 0:
            msb_first = False
        val = 0
        off_val = 0
        # print(var_name, bits, count)
        for i in range(count):
            # print(i, bits[i], 2**(count-i-1))
            val += bits[i] * (2 ** (count - i - 1))
            off_val += off_bits[i] * (2 ** (count - i - 1))
        # print(var_name, count, val, '{:0{width}b}'.format(val, width=count))
        SCAN_LIST.append(ScanBit(domain, var_name, count, int(val), off_bits=int(off_val), msb_first=msb_first))
        if print_info:
            print(
                f'Wrote to buffer \'{var_name: >35}[{count - recorded_bit_index - 1}:{recorded_bit_index}]\' with 0b{val:>0{count}b},'
                f' Unsigned Decimal Val = {val}, '
                f' Off value Decimal = {off_val}, '
                f'msb_first={1 if msb_first else 0}.')

    print('Scan buffer preparation finished, ' + str(scan_count) + ' bits loaded.')
    # return scan_count, scan_buffer, SCAN_LIST
    return scan_count, SCAN_LIST


# write value
def scan_write(ser, scan_string):
    # actual scan write
    msg = ''
    if not Emulating:
        while msg != MSG_WRITE_COMPLETE:
            while msg != MSG_WRITE:
                # print('inner loop MSG: ' + msg + '.')
                ser.write(CMD_WRITE)
                time.sleep(0.4)
                msg = read_buffer(ser)

            # print("got MSG \'"+ msg + "\', Writing...")
            time.sleep(0.4)
            ser.write(scan_string.encode('utf-8'))
            time.sleep(0.4)
            msg = read_buffer(ser)
            # print("MSG :" + msg)

        print_msg(msg)

        # Execute the load command to latch values inside chip
        print("Starting Load")
        ser.write(CMD_LOAD)
        # time.sleep(0.01)
        print_msg(read_buffer(ser))
    else:
        print("[Emulating] Starting Load")
        print_msg('[Emulating] Message written.')


# Read All Scan bits from chip
def scan_read(ser):
    # Read back the scan chain contents
    if not Emulating:
        print("Starting Read")
        ser.write(CMD_READ)
        time.sleep(0.75)
        read_data = read_buffer(ser)
        return read_data
    else:
        print("[Emulating] Starting Read")
        time.sleep(1)
        return ''


# Format the array of ScanBit objects to a single scanbit string
def scan_format(scan_count, SCAN_LIST):
    scan_buffer = []
    for scan in reversed(list(SCAN_LIST)):
        unfolded_list = unfold_bits_scan_write(scan.bit_width, scan.bits_string)
        for bit_array in reversed(list(unfolded_list)):
            scan_buffer.append(bit_array)
    padding_zeros = [0 for n in range(scanchain_size - scan_count)]
    scan_arr = np.array(scan_buffer)
    scan_arr = np.concatenate((scan_arr, padding_zeros))
    scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
    # scan_arr = [1 for n in range(scanchain_size)]
    # scan_arr[-1] = int(np.round(np.random.rand()))

    print(str(len(padding_zeros)) + ' padding 0 bits padded, total message size is '
          + str(len(scan_arr)) + ' bits, begin writing...\n')
    scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
    return scan_string


# Write and Read
def scan_write_and_read(ser, scan_count, SCAN_LIST):
    scan_string = scan_format(scan_count, SCAN_LIST)

    # print(scan_string.encode('utf-8'))

    # Write
    scan_write(ser, scan_string)

    # Read
    if not Emulating:
        read_data = scan_read(ser)
    else:
        print('[Emulating] reading from buffer')
        read_data = scan_string

    if scan_string == read_data:
        print("SUCCESS: Read matches write")
        if print_info:
            print_msg('[Expecting]:')
            print_msg(textwrap.fill(scan_string, width=100))
            print_msg('[Got]:')
            print_msg(textwrap.fill(read_data, width=100))
    else:
        error_msg("FAILURE: Read/write comparison incorrect")
        if print_info:
            error_msg('[Expecting]:')
            error_msg(textwrap.fill(scan_string, width=100))
            error_msg('[Got]:')
            error_msg(textwrap.fill(read_data, width=100))

    if print_info:
        print('End of Scan Write.')


# Open the CSV file in read mode
def scan_init(csv_path):
    # ser.set_buffer_size(rx_size=2000, tx_size=2000)
    time.sleep(0.1)
    # load up the scan buffer
    with open(csv_path) as file_obj:
        reader_obj = csv.reader(file_obj)
        scan_count, SCAN_LIST = csv_to_ScanBit(reader_obj)

    return scan_count, SCAN_LIST


# Modify value in the scan chain
def modify_val(SCAN_LIST, signal_name, val):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        found_object.set_val(val)
        bit_index = f'{signal_name}[{found_object.bit_width - 1}:{0}]' if found_object.msb_first \
            else f'{signal_name}[{0}:{found_object.bit_width - 1}]'
        if print_info:
            print(f'Updated value for {bit_index: >35} = {found_object.value: >15}, bit = {found_object.bits_string}')
            # print(f"Updated value for {signal_name}: {found_object.value}")
    else:
        print(f"No object found with name '{signal_name}'")


# set scan chain values to off_bits
def turn_off(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        found_object.set_val(found_object.off_bits)
        bit_index = f'{signal_name}[{found_object.bit_width - 1}:{0}]' if found_object.msb_first \
            else f'{signal_name}[{0}:{found_object.bit_width - 1}]'
        if print_info:
            print(f'Updated value for {bit_index: >35} = {found_object.value: >15}, bit = {found_object.bits_string}')
    else:
        print(f"No object found with name '{signal_name}'")


def group_op(ser, scan_count, SCAN_LIST, group_name, op):
    if op == 'on' or op == 'off':
        for scans in SCAN_LIST:
            cmd_name = scans.signal_name
            if cmd_name[0:2] == group_name:
                modify_val(SCAN_LIST, cmd_name, scans.default_val if op == 'on' else scans.off_bits)
        scan_write_and_read(ser, scan_count, SCAN_LIST)
    elif op == 'ls':
        for scans in SCAN_LIST:
            cmd_name = scans.signal_name
            if cmd_name[0:2] == group_name:
                bit_index = f'{cmd_name}[{scans.bit_width - 1}:{0}]' if scans.msb_first \
                    else f'{cmd_name}[{0}:{scans.bit_width - 1}]'
                print(f'{bit_index: >35} = {scans.value: >15}, bit = {scans.bits_string}')
    elif op == 'step':
        for scans in SCAN_LIST:
            cmd_name = scans.signal_name
            if cmd_name[0:2] == group_name:
                modify_val(SCAN_LIST, cmd_name, scans.off_bits)
                scan_write_and_read(ser, scan_count, SCAN_LIST)


def fetch_val(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        val = found_object.get_val()
        print(f"Stored value for {signal_name}: {val}")
        return val, found_object.msb_first
    else:
        print(f"No object found with name '{signal_name}'")
        return 0xDEADBEEF,


def fetch_def_val(SCAN_LIST, signal_name):
    found_object = next((obj for obj in SCAN_LIST if obj.signal_name == signal_name), None)
    if found_object:
        def_val = found_object.get_def_val()
        print(f"Stored def value for {signal_name}: {def_val}")
        return def_val, found_object.msb_first
    else:
        print(f"No object found with name '{signal_name}'")
        return 0xDEADBEEF, 0xDEADBEEF


# Main
if __name__ == "__main__":
    curr_msb = scan_data_size - 1
    with serial.Serial(port, baudrate=baudrate, timeout=None) as my_ser:
        my_scan_count, my_SCAN_LIST = scan_init(csv_name)
        scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)

        root = tk.Tk()
        root.winfo_toplevel().title("SenDar Scanbits Control Dashboard by Yikuan Chen 2024")
        root.geometry(f'{w_size}x{h_size}')
        # style = ThemedStyle(root)
        # style.set_theme("arc")
        app = DataGUI(root, csv_name, my_ser, my_scan_count, my_SCAN_LIST)
        root.mainloop()

        # target_name = 'TX_DCOC_CTRL_Q'
        # old_val = fetch_val(my_SCAN_LIST, target_name)
        # new_value = 0b0011111
        #
        # # modify the scan chain value and re-write the chain
        # modify_val(my_SCAN_LIST, target_name, new_value)
        #
        # old_val = fetch_val(my_SCAN_LIST, target_name)
        # scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
        stop_flag = False
        while stop_flag == False:
            task = input("Enter Command:\n")
            task = task.split()
            if len(task) < 1:
                continue
            if task[0] == 'q':
                stop_flag = True
            if task[0] == 'reset':
                my_scan_count, my_SCAN_LIST = scan_init(csv_name)
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'step':
                for scans in my_SCAN_LIST:
                    cmd_name = scans.signal_name
                    modify_val(my_SCAN_LIST, cmd_name, 0)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'zz':  # turn off, set to nominal vals
                for scans in my_SCAN_LIST:
                    cmd_name = scans.signal_name
                    # modify_val(my_SCAN_LIST, cmd_name, 0)
                    turn_off(my_SCAN_LIST, cmd_name)
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'zero':
                scan_arr = [0 for n in range(scanchain_size)]
                scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
                print('Writing all zeros to the scanchain\n')
                scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
                scan_write(my_ser, scan_string)
            if task[0] == 'ones':
                scan_arr = [1 for n in range(scanchain_size)]
                scan_arr = np.subtract(np.ones(scanchain_size), scan_arr)
                print('Writing all ones to the scanchain\n')
                scan_string = "".join(map(lambda x: str(int(x)), scan_arr))
                scan_write(my_ser, scan_string)
            if task[0] == 'set':
                if len(task) != 3:
                    continue
                cmd_name = task[1]
                if task[2] == 'def':
                    val, msb_first = fetch_def_val(my_SCAN_LIST, cmd_name)
                elif task[2] == 'off':
                    turn_off(my_SCAN_LIST, cmd_name)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
                    continue
                else:
                    val = task[2]
                old_val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {old_val}, msb_first = {msb_first}')
                modify_val(my_SCAN_LIST, cmd_name, int(val))
                new_val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {new_val}, msb_first = {msb_first}')
                scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'get':
                cmd_name = task[1]
                val, msb_first = fetch_val(my_SCAN_LIST, cmd_name)
                print(f'Value for {cmd_name} is {val}, msb_first = {msb_first}')
            if task[0] == 'LO' or task[0] == 'RX' or task[0] == 'VM' or task[0] == 'TX':
                group_op(my_ser, my_scan_count, my_SCAN_LIST, group_name=task[0], op=task[1])
            if task[0] == 'PA':
                if task[1] == 'on' or task[1] == 'off':
                    # TX_IB_PA
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:8] == 'TX_IB_PA':
                            modify_val(my_SCAN_LIST, cmd_name, scans.default_val if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'TX_DCOC':
                if task[1] == 'on' or task[1] == 'off':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:9] == 'TX_DCOC_SP': # default turn on positive
                            modify_val(my_SCAN_LIST, cmd_name, 1 if task[1] == 'on' else scans.off_bits)
                        elif cmd_name[0:13] == 'TX_DCOC_CTRL_':
                            if scans.bit_width > 1:
                                modify_val(my_SCAN_LIST, cmd_name, 32 if task[1] == 'on' else scans.off_bits)
                            else:
                                modify_val(my_SCAN_LIST, cmd_name, 0)

                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
            if task[0] == 'VM_DCOC':
                if task[1] == 'on' or task[1] == 'off':
                    for scans in my_SCAN_LIST:
                        cmd_name = scans.signal_name
                        if cmd_name[0:9] == 'VM_DCOC_SP':
                            modify_val(my_SCAN_LIST, cmd_name, 1 if task[1] == 'on' else scans.off_bits)
                        elif cmd_name[0:13] == 'VM_DCOC_CTRL_':
                            if scans.bit_width > 1:
                                modify_val(my_SCAN_LIST, cmd_name, 32 if task[1] == 'on' else scans.off_bits)
                    scan_write_and_read(my_ser, my_scan_count, my_SCAN_LIST)
