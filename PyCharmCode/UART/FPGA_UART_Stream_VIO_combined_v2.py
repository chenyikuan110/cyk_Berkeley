#!/usr/bin/env python3
import os
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time
import threading
import tkinter as tk
import ctypes
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# try:
#     ctypes.windll.shcore.SetProcessDpiAwareness(1)
# except:
#     ctypes.windll.user32.SetProcessDPIAware()

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


class vio_param:
    def __init__(self, cmd, default_val, addr, width, conv_factor=1, unit=''):
        self.cmd = cmd
        self.addr = addr
        self.width = width
        self.default_val = default_val
        self.curr_val = default_val
        self.conv_factor = conv_factor
        self.unit = unit


# Windows
emulation_on = False
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM7' if emulation_on else 'COM9'  # CHANGE THIS COM PORT 7 is emulation, 9 is FPGA here
    ser.timeout = 2
    ser.open()
else:
    ser = serial.Serial('/dev/ttys002')
    ser.baudrate = 115200  # 921600

# emulation enable

emulation_fft = False
multiply_factor = 1
plot_individual_bits = False
bit_index = 0
plot_on = True
scale_FS = False
print_stream_msg = False
display_freq = False
aggregate = False
aggregate_size = 16
scale = 1 << 15
decimation = 1

# GUI
w_size = 900
h_size = 800

# Prepare serial read parameters
LUT_size = 32768
array_length = 512
bytes_per_number = 2
num_channels = 2
transmit_length = array_length * bytes_per_number * num_channels
plot_length = array_length

fsample_DAC = 80E6
fund_tone = fsample_DAC / 4 / LUT_size

fsample_ADC = 10E6

ADC_clip_threshold = 65535

Downsample_factor = 8

# default params
start_up_params = []
start_up_params.append(vio_param('TX_DAC_frequency_word', 16384, 0, 3, fund_tone, 'Hz'))
start_up_params.append(vio_param('TX_DAC_initial_phase', 0, 3, 3, 1 / (LUT_size / 90), 'deg'))
start_up_params.append(vio_param('TX_IQ_phase_diff', 32767, 6, 3, 1 / (LUT_size / 90), 'deg'))
start_up_params.append(vio_param('TX_Mult_enable', 1, 9, 1))
start_up_params.append(vio_param('TX_Mult_gain', 2048, 10, 3))
start_up_params.append(vio_param('VM_DAC_frequency_word', 16384, 13, 3, fund_tone, 'Hz'))
start_up_params.append(vio_param('VM_DAC_initial_phase', 0, 16, 3, 1 / (LUT_size / 90), 'deg'))
start_up_params.append(vio_param('VM_IQ_phase_diff', 32767, 19, 3, 1 / (LUT_size / 90), 'deg'))
start_up_params.append(vio_param('VM_Mult_enable', 1, 22, 1))
start_up_params.append(vio_param('VM_Mult_gain', 400, 23, 3))
start_up_params.append(vio_param('ADC_clip_threshold', 65535, 26, 2))
start_up_params.append(vio_param('Downsample_factor', 8, 28, 1))

# dict_cmd = {
#     'TX_DAC_frequency_word': [0, 2, 6]
#     , 'TX_DAC_initial_phase': [2, 2, 0]
#     , 'TX_IQ_phase_diff': [4, 2, 16384]
#     , 'TX_Mult_enable': [6, 1, 1]
#     , 'TX_Mult_gain': [7, 3, 16383]
#     , 'VM_DAC_frequency_word': [10, 2, 6]
#     , 'VM_DAC_initial_phase': [12, 2, 0]
#     , 'VM_IQ_phase_diff': [14, 2, 16384]
#     , 'VM_Mult_enable': [16, 1, 1]
#     , 'VM_Mult_gain': [17, 3, 16383]
# } # old, when there's only 14-bit freq word

# Prepare byte-to-integer conversion
dt = np.dtype(np.int16)
dt = dt.newbyteorder('>')


# input("Open a serial program in another terminal, then hit Enter")

# input("Open a serial program in another terminal, then hit Enter")


# Helper func
# for emulation
def generate_byte_array(size):
    # Initialize an empty byte array
    global print_stream_msg
    if print_stream_msg:
        print('Generating bytes')
    byte_array = bytearray(size)

    data = np.zeros(int(size / 2))
    for i in range(int(size / 2)):
        data[i] = int(np.sin(((i % 1024) / 80) * (1 + 0.01 * np.random.rand())) * 8192 + np.random.rand() * 0)

    global emulation_fft
    if emulation_fft:
        data = np.fft.fft(data) / (4 * 4 * 4 * 4 * 4)

    for i in range(size):
        index = int(i / 4)
        if i % 4 == 0:
            byte_array[i] = (int(np.imag(data[index])) & 0xFF00) >> 8  # IM_MSB
        elif i % 4 == 1:
            byte_array[i] = int(np.imag(data[index])) & 0x00FF  # IM_LSB
        elif i % 4 == 2:
            byte_array[i] = (int(np.real(data[index])) & 0xFF00) >> 8  # RE_MSB
        elif i % 4 == 3:
            byte_array[i] = int(np.real(data[index])) & 0x00FF  # RE_LSB

    return byte_array


# Calculate an average array
def average_arrays(arrays):
    # Convert list of arrays to a NumPy array for easy element-wise operations
    np_arrays = np.array(arrays)
    # Calculate the element-wise average
    average_array = np.mean(np_arrays, axis=0)
    return average_array


# print with color utility
def highlight_msg(msg):
    global bcolors
    if 'Error' in msg:
        return bcolors.WARNING + msg + bcolors.ENDC
    else:
        return bcolors.OKGREEN + msg + bcolors.ENDC


# split up the number to bytes for UART transmission
def int_to_bytes(num, width):
    byte_array = []
    if num < 0:
        num = 2 ** (8 * width) + num
    for ii in range(width):
        byte_array.append(num & 0X00FF)
        num = int(num >> 8)
    return byte_array  # [::-1] # because I flipped the endianess in verilog


# for command to addr conversion
def parse_cmd(cmd, val, rootGUI=None):
    global start_up_params
    curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)

    start_addr = curr_param.addr
    width = curr_param.width
    default_val = curr_param.default_val
    address = [n for n in reversed(range(start_addr, start_addr + width))]
    curr_param.curr_val = val
    # print(cmd, val, address, int_to_bytes(val, width))
    # print(rootGUI)
    if rootGUI:
        # update plot
        if curr_param.cmd == 'TX_DAC_initial_phase':
            actual_val = val / (LUT_size*2 / np.pi)
            # print(np.cos(actual_val),np.sin(actual_val))
            rootGUI.TX_phasemag.set_offsets(np.c_[np.cos(actual_val),np.sin(actual_val)])
            rootGUI.canvas_IQ.draw()
        elif curr_param.cmd == 'VM_DAC_initial_phase':
            actual_val = val / (LUT_size*2 / np.pi)
            # print(np.cos(actual_val),np.sin(actual_val))
            rootGUI.VM_phasemag.set_offsets(np.c_[np.cos(actual_val),np.sin(actual_val)])
            rootGUI.canvas_IQ.draw()


    return address, int_to_bytes(val, width), int_to_bytes(default_val, width)


# reset value
def reset_all(rootGUI=None):
    global start_up_params
    addr = []
    val = []
    cmds = []
    # for cmd_keys, cmd_vals in dict_cmd.items():
    for params in start_up_params:
        addr_, ignore, val_ = parse_cmd(params.cmd, params.default_val,rootGUI)
        addr.append(addr_)
        val.append(val_)
        cmds.append(params.cmd)
    return cmds, np.concatenate(addr), np.concatenate(val)

# for re-programming
def get_all():
    global start_up_params
    addr = []
    val = []
    cmds = []
    # for cmd_keys, cmd_vals in dict_cmd.items():
    for params in start_up_params:
        addr_, val_ , ignore_ = parse_cmd(params.cmd, params.curr_val)
        addr.append(addr_)
        val.append(val_)
        cmds.append(params.cmd)
    return cmds, np.concatenate(addr), np.concatenate(val)

# send msg
def send_to_dut(port, addr, val):
    global emulation_on

    for i in reversed(range(len(addr))):
        msg = '[sending] ' + str(val[i]) + ' to address ' \
              + str(addr[i]) + ': ' + str(49) + ' ' + str(addr[i]) + ' ' + str(val[i])
        print(highlight_msg(msg))
        if not emulation_on:
            port.write(bytearray([49, addr[i], val[i]]))
        time.sleep(0.01)


# define the GUI class
class data_GUI:
    def __init__(self, root):

        global multiply_factor
        global ADC_clip_threshold
        global Downsample_factor
        global display_freq
        global aggregate
        global aggregate_size
        global plot_individual_bits
        global bit_index
        global aggregate
        global aggregate_size
        global scale_FS
        global scale

        # this flag kills both threads
        self.quit_flag = False
        self.window_show = True
        self.scale_FS = tk.BooleanVar(value=scale_FS)
        self.scale = scale
        self.plot_frequency = tk.BooleanVar(value=display_freq)
        self.aggregate = tk.BooleanVar(value=aggregate)
        self.aggregate_size = aggregate_size
        self.ADC_clip_threshold = ADC_clip_threshold
        self.Downsample_factor = Downsample_factor

        # Internalize
        self.root = root

        # Title
        self.Titlelabel = tk.Label(self.root, text=f"SenDar ADC Display v2.0", font=("Arial", 15, "bold"))
        self.Titlelabel.grid(column=0, row=0, sticky="ew")

        # Checkbox frame
        self.CB_Frame = ttk.Frame(self.root)
        self.CB_Frame.grid(row=1, column=0, sticky='ew')

        # Create a frame for the Matplotlib figure
        self.Plot_Frame = ttk.Frame(self.root)
        self.Plot_Frame.grid(row=2, column=0, sticky='news')

        # Create a frame for configs
        self.Option_Frame = ttk.Frame(self.root)
        self.Option_Frame.grid(row=3, column=0, sticky='news')

        # Visibility checkbox
        self.var_I_data = tk.BooleanVar(value=True)
        self.var_Q_data = tk.BooleanVar(value=True)
        self.var_Mag = tk.BooleanVar(value=True)
        self.var_Phase = tk.BooleanVar(value=False)
        self.var_Peak = tk.BooleanVar(value=False)

        self.cb_I_data = ttk.Checkbutton(self.CB_Frame, text="I_data", variable=self.var_I_data,
                                         command=self.toggle_curve)
        self.cb_Q_data = ttk.Checkbutton(self.CB_Frame, text="Q_data", variable=self.var_Q_data,
                                         command=self.toggle_curve)
        self.cb_Mag = ttk.Checkbutton(self.CB_Frame, text="Magnitude", variable=self.var_Mag, command=self.toggle_curve)
        self.cb_Phase = ttk.Checkbutton(self.CB_Frame, text="Phase", variable=self.var_Phase, command=self.toggle_curve)
        self.cb_Peak = ttk.Checkbutton(self.CB_Frame, text="Show Peak", variable=self.var_Peak, command=self.toggle_curve)

        self.cb_I_data.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.cb_Q_data.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        self.cb_Mag.grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.cb_Phase.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        self.cb_Peak.grid(row=0, column=4, sticky='w', padx=10, pady=5)

        # Define the data for curves
        self.x_range = range(0, plot_length, decimation)
        self.x_range_max = plot_length

        if self.plot_frequency.get():
            self.x_range_max = plot_length / array_length * fsample_ADC / 2
        self.x_range_plot = [x * (self.x_range_max / plot_length) for x in self.x_range]

        self.x_max = self.x_range_max
        self.x_min = 0
        self.y_max = 40000 if not self.scale_FS.get() else 40000/self.scale
        self.y_min = -40000 if not self.scale_FS.get() else -40000/self.scale
        self.y3_min = -20
        self.y3_max = 380

        self.aggregated_results_I = []
        self.aggregated_results_Q = []

        # Plot initial curves
        # Create a figure and axis for plotting
        self.fig, self.ax = plt.subplots()
        self.ax.patch.set_facecolor('black')
        self.I_data, = self.ax.plot(self.x_range_plot, np.linspace(0, 0, len(self.x_range_plot)), label='I')
        self.Q_data, = self.ax.plot(self.x_range_plot, np.linspace(0, 0, len(self.x_range_plot)), label='Q')
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')


        self.ax2 = self.ax.twinx()
        self.Mag, = self.ax2.plot(self.x_range_plot, np.linspace(0, 0, len(self.x_range_plot)), color='yellow',
                                  label='Magnitude dB')

        self.y2_min = -10 - 20 * np.log10(self.scale)
        self.y2_max = 100
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax2.set_ylim(self.y2_min, self.y2_max)
        self.ax2.tick_params(axis='y', labelcolor='#c7a118')

        self.ax3 = self.ax.twinx()
        self.ax3.spines['right'].set_position(('outward', 30))
        self.Phase, = self.ax3.plot(self.x_range_plot, np.linspace(0, 0, len(self.x_range_plot)), color='red',
                                   label='Phase')
        self.ax3.set_ylim(self.y3_min, self.y3_max)
        self.ax3.tick_params(axis='y', labelcolor='tab:red')

        # Peak
        self.peakpt_dB = self.ax2.scatter([], [], color='r', marker='o')

        # Add legend
        handles, labels = self.ax.get_legend_handles_labels()
        handles2, labels2 = self.ax2.get_legend_handles_labels()
        handles3, labels3 = self.ax3.get_legend_handles_labels()

        # Add handles and labels from the second axis to the first
        handles += handles2
        labels += labels2
        handles += handles3
        labels += labels3
        self.ax.legend(handles, labels, loc='lower center',facecolor=(1,1,1,0.5))
        # self.ax2.legend()

        # Add to Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.Plot_Frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky='nsew')
        self.Plot_Frame.bind("<Configure>", self.on_resize)

        # Set the visibility
        self.toggle_curve()

        # Configure bottom frame grid layout
        self.Plot_Frame.grid_rowconfigure(0, weight=1)
        self.Plot_Frame.grid_columnconfigure(0, weight=1)

        # Configure the Option Frame
        self.Option_subframe = tk.Frame(self.Option_Frame)
        self.Option_subframe.grid(row=0, column=0, padx=5, sticky='w')

        self.Slider_subframe = tk.Frame(self.Option_Frame)
        self.Slider_subframe.grid(row=1, column=0, padx=5, sticky='w')

        self.IQ_subframe = tk.Frame(self.Option_Frame)
        self.IQ_subframe.grid(row=1, column=1, padx=5, sticky='news')

        # Unit
        self.freq_plot_button = ttk.Checkbutton(self.Option_subframe, text="Plot Frequency (Hz)",
                                                variable=self.plot_frequency,
                                                command=self.toggle_unit)
        self.freq_plot_button.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        # Aggregate (More Averaging)
        self.aggregate_button = ttk.Checkbutton(self.Option_subframe, text="Aggregate", variable=self.aggregate,
                                                command=self.toggle_aggregate)
        self.aggregate_button.grid(row=0, column=1, sticky='e', padx=10, pady=5)
        self.aggregate_size_entry = tk.Entry(self.Option_subframe)
        self.aggregate_size_entry.insert(0, f'{self.aggregate_size}')
        self.aggregate_size_entry.grid(row=0, column=2, padx=5)
        self.aggregate_size_entry.bind("<FocusOut>", lambda e: self.update_aggregate_size())

        # Threshold
        self.ADC_clip_threshold_label = tk.Label(self.Option_subframe, text="ADC clip threshold")
        self.ADC_clip_threshold_label.grid(row=1, column=0, padx=5, sticky='w')
        self.ADC_clip_threshold_entry = tk.Entry(self.Option_subframe)
        self.ADC_clip_threshold_entry.insert(0, f'{self.ADC_clip_threshold}')
        self.ADC_clip_threshold_entry.grid(row=1, column=1, padx=5, sticky='w')
        self.ADC_clip_threshold_button = ttk.Button(self.Option_subframe, text="Update Value", 
                                                command=self.update_ADC_clip_threshold)
        self.ADC_clip_threshold_button.grid(row=1, column=2, sticky='w', padx=10, pady=5)

        # self.ADC_clip_threshold_entry.bind("<FocusOut>", lambda e: self.update_ADC_clip_threshold())

        # Downsample_factor
        self.Downsample_factor_label = tk.Label(self.Option_subframe, text="Downsample_factor")
        self.Downsample_factor_label.grid(row=2, column=0, padx=5, sticky='w')
        self.Downsample_factor_entry = tk.Entry(self.Option_subframe)
        self.Downsample_factor_entry.insert(0, f'{self.Downsample_factor}')
        self.Downsample_factor_entry.grid(row=2, column=1, padx=5, sticky='w')
        self.Downsample_factor_button = ttk.Button(self.Option_subframe, text="Update Value", 
                                                command=self.update_Downsample_factor)
        self.Downsample_factor_button.grid(row=2, column=2, sticky='w', padx=10, pady=5)
        # self.Downsample_factor_entry.bind("<FocusOut>", lambda e: self.update_Downsample_factor())

        # Scale Toggle (normalization)
        self.aggregate_button = ttk.Checkbutton(self.Option_subframe, text="Normalize Plot", variable=self.scale_FS,
                                                command=self.toggle_scale_FS)
        self.aggregate_button.grid(row=1, column=3, sticky='w', padx=10, pady=5)

        # ----- Sliders ------
        # X
        self.xlim_frame = tk.Frame(self.Slider_subframe)
        self.xlim_frame.grid(row=0, column=0, sticky='nsew', pady=5)
        # Create sliders and textboxes for x-axis limits
        self.xlim_label = tk.Label(self.xlim_frame, text="X Limits (min,max):")
        self.xlim_label.grid(row=0, column=0, padx=5)

        self.xlim_entry = tk.Entry(self.xlim_frame)
        self.xlim_entry.insert(0, f'{self.x_min},{self.x_max}')
        self.xlim_entry.grid(row=0, column=1, padx=5)

        self.xlim_min_slider = tk.Scale(self.xlim_frame, from_=0, to=self.x_max, orient=tk.HORIZONTAL,
                                        label="X Limit Min")
        self.xlim_min_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.xlim_min_slider.set(self.x_min)
        self.xlim_min_slider.grid(row=0, column=2, padx=5)
        self.xlim_max_slider = tk.Scale(self.xlim_frame, from_=0, to=self.x_max, orient=tk.HORIZONTAL,
                                        label="X Limit Max")
        self.xlim_max_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.xlim_max_slider.set(self.x_max)
        self.xlim_max_slider.grid(row=0, column=3, padx=5)

        # Y
        self.ylim_frame = tk.Frame(self.Slider_subframe)
        self.ylim_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        # Create sliders and textboxes for x-axis limits
        self.ylim_label = tk.Label(self.ylim_frame, text="Y Limits (min,max):")
        self.ylim_label.grid(row=0, column=0, padx=5)

        self.ylim_entry = tk.Entry(self.ylim_frame)
        self.ylim_entry.insert(0, f'{self.y_min},{self.y_max}')
        self.ylim_entry.grid(row=0, column=1, padx=5)

        self.ylim_min_slider = tk.Scale(self.ylim_frame, from_=self.y_min, to=self.y_max, orient=tk.HORIZONTAL,
                                        label="Y Limit Min")
        self.ylim_min_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.ylim_min_slider.set(self.y_min)
        self.ylim_min_slider.grid(row=0, column=2, padx=5)
        self.ylim_max_slider = tk.Scale(self.ylim_frame, from_=self.y_min, to=self.y_max, orient=tk.HORIZONTAL,
                                        label="Y Limit Max")
        self.ylim_max_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.ylim_max_slider.set(self.y_max)
        self.ylim_max_slider.grid(row=0, column=3, padx=5)
        self.ylim_min_slider.configure(resolution=1 / self.scale if self.scale_FS.get() else 1)
        self.ylim_max_slider.configure(resolution=1 / self.scale if self.scale_FS.get() else 1)

        # Y2
        self.ylim2_frame = tk.Frame(self.Slider_subframe)
        self.ylim2_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        # Create sliders and textboxes for x-axis limits
        self.ylim2_label = tk.Label(self.ylim2_frame, text="Y Limits (min,max):")
        self.ylim2_label.grid(row=0, column=0, padx=5)

        self.ylim2_entry = tk.Entry(self.ylim2_frame)
        self.ylim2_entry.insert(0, f'{self.y2_min},{self.y2_max}')
        self.ylim2_entry.grid(row=0, column=1, padx=5)

        self.ylim2_min_slider = tk.Scale(self.ylim2_frame, from_=self.y2_min, to=self.y2_max, orient=tk.HORIZONTAL,
                                         label="Y Limit Min")
        self.ylim2_min_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.ylim2_min_slider.set(self.y2_min)
        self.ylim2_min_slider.grid(row=0, column=2, padx=5)
        self.ylim2_max_slider = tk.Scale(self.ylim2_frame, from_=self.y2_min, to=self.y2_max, orient=tk.HORIZONTAL,
                                         label="Y Limit Max")
        self.ylim2_max_slider.bind("<B1-Motion>", lambda event: self.update_limits_from_sliders())
        self.ylim2_max_slider.set(self.y2_max)
        self.ylim2_max_slider.grid(row=0, column=3, padx=5)

        # Bind textboxes to update sliders
        self.xlim_entry.bind("<FocusOut>", lambda e: self.update_limits_from_text())
        self.ylim_entry.bind("<FocusOut>", lambda e: self.update_limits_from_text())
        self.ylim2_entry.bind("<FocusOut>", lambda e: self.update_limits_from_text())

        # ---- IQ-plot ----     
        self.fig_IQ , self.ax_IQ = plt.subplots(figsize=(2.5,2.5))
        self.fig_IQ.patch.set_facecolor((0, 1, 1, 0.05))
        self.ax_IQ.patch.set_facecolor((0, 1, 1, 0.0))
        self.unit_circle_IQ = Circle((0, 0), 1, color='blue', alpha=0.2, fill=False, linestyle='--', linewidth=1.5)
        self.ax_IQ.add_patch(self.unit_circle_IQ)
        self.TX_phasemag = self.ax_IQ.scatter(1,0, label='TX',marker='o')
        self.VM_phasemag = self.ax_IQ.scatter(1,0, label='VM',marker='*')
        self.ax_IQ.set_xlim(-1.1, 1.1)
        self.ax_IQ.set_ylim(-1.1, 1.1)
        self.ax_IQ.set_xlabel('I',color='red',backgroundcolor=(1,0,0,0.1))
        self.ax_IQ.set_ylabel('Q',color='red',backgroundcolor=(0,0,1,0.1))
        self.ax_IQ.xaxis.set_label_coords(0.5,0.1)
        self.ax_IQ.yaxis.set_label_coords(0.1,0.5)
        self.ax_IQ.set_aspect('equal')
        self.ax_IQ.legend(loc='lower center',bbox_to_anchor=(0.5, -0.35), ncol=2, frameon=True, fontsize='small',facecolor=(0,0,1,0.1),framealpha=0.1)
        self.canvas_IQ = FigureCanvasTkAgg(self.fig_IQ, master=self.IQ_subframe)
        self.canvas_IQ_widget = self.canvas_IQ.get_tk_widget()
        self.canvas_IQ_widget.grid(row=0, column=0, padx=0, pady=3)
        self.ax_IQ.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
        
        # self.fig_IQ.set_size
        # self.fig_IQ.set_size_inches(1,1, forward=True)
        # self.canvas_IQ_widget.place(relx=0.5, rely=0.5, anchor='center')
        self.fig_IQ.tight_layout(pad=1.0)
        self.fig_IQ.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.2)
        self.canvas_IQ.draw()
        self.IQ_subframe.update_idletasks()
        self.IQ_subframe.grid_propagate(False) 

        # Configure bottom frame grid layout
        # self.IQ_subframe.grid_rowconfigure(0, weight=0)
        # self.IQ_subframe.grid_columnconfigure(0, weight=0)


        # Configure root grid layout
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Start the thread for updating the plot
        self.vio_thread = threading.Thread(target=self.run_vio)
        self.vio_thread.start()

        self.count = 0
        # self.update_thread = threading.Thread(target=self.fpga_stream_old())
        self.update_thread = threading.Thread(target=self.receive_data)
        self.update_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # add a flag monitor
        self.root.after(1, self.check_quit_flag())

        print("Running...")

    def safe_destroy(self):
        try:
            print("Destroying root...")
            self.update_thread.join()
            self.vio_thread.join()
            self.root.quit()
        except Exception as e:
            print(f"Error while destroying root: {e}")

    def check_quit_flag(self, event=None):
        if self.quit_flag:
            self.update_thread.join()
            self.vio_thread.join()
            print('Quit detected, Cleaning up...')
            self.root.after(0, self.safe_destroy)

        else:
            self.root.after(1, self.check_quit_flag)

    def on_closing(self):
        self.window_show = False
        self.update_thread.join()
        self.root.withdraw()
        print('Window closed, use VIO command line to quit')

    def on_resize(self, event):
        # Adjust the figure size to match the canvas size
        canvas_width = self.canvas_widget.winfo_width()
        canvas_height = self.canvas_widget.winfo_height()
        self.fig.set_size_inches(canvas_width / 100, canvas_height / 100, forward=True)
        # self.fig.tight_layout()
        self.canvas.draw()

    # Function to update the plot limits based on the sliders
    def update_limits_from_sliders(self):
        self.x_min = self.xlim_min_slider.get()
        self.x_max = self.xlim_max_slider.get()
        self.y_min = self.ylim_min_slider.get()
        self.y_max = self.ylim_max_slider.get()
        self.y2_min = self.ylim2_min_slider.get()
        self.y2_max = self.ylim2_max_slider.get()

        self.xlim_min_slider.configure(from_=0, to=self.x_max - 1)
        self.xlim_max_slider.configure(from_=self.x_min+1, to=self.x_range_max)
        self.ylim_min_slider.configure(from_=-40000 if not self.scale_FS.get() else -40000/self.scale,
                                       to=self.y_max - (1 if not self.scale_FS.get() else 1/self.scale))
        self.ylim_max_slider.configure(from_=self.y_min+(1 if not self.scale_FS.get() else 1/self.scale),
                                       to=40000 if not self.scale_FS.get() else 40000/self.scale)
        self.ylim2_min_slider.configure(from_=-10 - 20 * np.log10(self.scale),to=self.y2_max - 1)
        self.ylim2_max_slider.configure(from_=self.y2_min, to=100)

        self.ax.set_xlim([self.x_min, self.x_max])
        self.ax.set_ylim([self.y_min, self.y_max])
        self.ax2.set_ylim([self.y2_min, self.y2_max])

        self.canvas.draw()
        # Update textboxes when sliders are changed
        self.xlim_entry.delete(0, tk.END)
        self.xlim_entry.insert(0, f"{self.x_min},{self.x_max}")
        self.ylim_entry.delete(0, tk.END)
        self.ylim_entry.insert(0, f"{self.y_min},{self.y_max}")
        self.ylim2_entry.delete(0, tk.END)
        self.ylim2_entry.insert(0, f"{self.y2_min},{self.y2_max}")

    def update_limits_from_text(self):
        try:
            xlim = list(map(float, self.xlim_entry.get().split(',')))
            ylim = list(map(float, self.ylim_entry.get().split(',')))
            ylim2 = list(map(float, self.ylim2_entry.get().split(',')))

            self.xlim_min_slider.set(xlim[0])
            self.xlim_max_slider.set(xlim[1])
            self.ylim_min_slider.set(ylim[0])
            self.ylim_max_slider.set(ylim[1])
            self.ylim2_min_slider.set(ylim2[0])
            self.ylim2_max_slider.set(ylim2[1])

            self.x_min = self.xlim_min_slider.get()
            self.x_max = self.xlim_max_slider.get()
            self.y_min = self.ylim_min_slider.get()
            self.y_max = self.ylim_max_slider.get()
            self.y2_min = self.ylim2_min_slider.get()
            self.y2_max = self.ylim2_max_slider.get()

            self.ax.set_xlim([self.x_min, self.x_max])
            self.ax.set_ylim([self.y_min, self.y_max])
            self.ax2.set_ylim([self.y2_min, self.y2_max])
            self.canvas.draw()

        except:
            pass

    def toggle_curve(self):
        self.I_data.set_visible(self.var_I_data.get())
        self.Q_data.set_visible(self.var_Q_data.get())
        self.Mag.set_visible(self.var_Mag.get())
        self.Phase.set_visible(self.var_Phase.get())
        self.peakpt_dB.set_visible(self.var_Peak.get())

        # Get the legend handles and labels
        handles, labels = self.ax.get_legend_handles_labels()
        handles2, labels2 = self.ax2.get_legend_handles_labels()
        handles3, labels3 = self.ax3.get_legend_handles_labels()

        # Add handles and labels from the second axis to the first
        handles += handles2
        handles += handles3
        labels += labels2
        labels += labels3

        new_handles = []
        new_labels = []
        # set legend
        for handle, label in zip(handles, labels):
            if handle.get_visible():
                new_handles.append(handle)
                new_labels.append(label)
        self.ax.legend(new_handles, new_labels, loc='lower center',facecolor=(1,1,1,0.5))
        self.canvas.draw()

    def toggle_unit(self):
        self.ax.relim()
        self.canvas.draw()

        # reset textbox
        # print('before',self.x_min, self.x_max)
        x_factor = fsample_ADC / 2 / plot_length
        self.x_range_max = plot_length
        if self.plot_frequency.get():
            self.x_range_max = plot_length / array_length * fsample_ADC / 2
        self.x_min = self.x_min * x_factor if self.plot_frequency.get() else self.x_min / x_factor
        self.x_max = self.x_max * x_factor if self.plot_frequency.get() else self.x_max / x_factor
        # print('after',self.x_min, self.x_max)

        # update sliders
        self.xlim_min_slider.configure(resolution=x_factor if self.plot_frequency.get() else 1,
                                       from_=0,
                                       to=self.x_max - (x_factor if self.plot_frequency.get() else 1))
        self.xlim_max_slider.configure(resolution=x_factor if self.plot_frequency.get() else 1,
                                       from_=self.x_min + (x_factor if self.plot_frequency.get() else 1),
                                       to=self.x_range_max)

        # self.ylim_min_slider.configure(from_=-40000 if not self.scale_FS else -40000/self.scale,
        #                                to=self.y_max - (1 if not self.scale_FS.get() else 1/self.scale))
        # self.ylim_max_slider.configure(from_=self.y_min + (1 if not self.scale_FS.get() else 1/self.scale),
        #                                to=40000 if not self.scale_FS else 40000/self.scale)

        self.xlim_min_slider.set(self.x_min)
        self.xlim_max_slider.set(self.x_max)
        # self.ylim_min_slider.set(self.y_min)
        # self.ylim_max_slider.set(self.y_max)

        # reset slider limits and textbox
        self.update_limits_from_sliders()

        # update plot labels
        self.ax.set_xlabel(f'Frequency (Hz)' if self.plot_frequency.get() else f'Frequency Bin Index')
        self.ax.set_xlim(self.x_min, self.x_max)
        self.ax.set_ylim(self.y_min, self.y_max)
        # self.ax2.set_ylim(self.y2_min, self.y2_max)
        # self.ax3.set_ylim(self.y3_min, self.y3_max)

        # update plot
        self.update_plot()
        print(f'Plot x-axis is bin-index' if not self.plot_frequency.get() else f'Plot x-axis is frequency (Hz).')

    def toggle_aggregate(self):
        print(f'Plot aggregated results.' if self.aggregate.get() else f'Plot raw results from FPGA.')

    def toggle_scale_FS(self):
        curr_y_min = self.ylim_min_slider.get()
        curr_y_max = self.ylim_max_slider.get()
        self.ylim_min_slider.configure(from_=-40000 if not self.scale_FS.get() else -40000 / self.scale,
                                       to=self.y_max - (1 if not self.scale_FS.get() else 1/self.scale))
        self.ylim_max_slider.configure(from_=self.y_min + (1 if not self.scale_FS.get() else 1/self.scale),
                                       to=40000 if not self.scale_FS.get() else 40000 / self.scale)

        self.ylim_min_slider.configure(resolution=1/self.scale if self.scale_FS.get() else 1)
        self.ylim_max_slider.configure(resolution=1/self.scale if self.scale_FS.get() else 1)
        self.ylim_min_slider.set(curr_y_min/self.scale if self.scale_FS.get() else curr_y_min*self.scale)
        self.ylim_max_slider.set(curr_y_max/self.scale if self.scale_FS.get() else curr_y_max*self.scale)

        self.update_limits_from_sliders()
        print(f'Plot scale in raw integer bits.' if self.scale_FS.get() else f'Plot scale normalized.')

    def update_aggregate_size(self):
        # get value
        self.aggregate_size = int(self.aggregate_size_entry.get())

    # ADC clip threshold
    def update_ADC_clip_threshold(self):
        # get value
        self.ADC_clip_threshold = int(self.ADC_clip_threshold_entry.get())

        # write vio
        curr_param = next((obj for obj in start_up_params if obj.cmd == 'ADC_clip_threshold'), None)
        addr, val, ignore = parse_cmd('ADC_clip_threshold', self.ADC_clip_threshold)
        send_to_dut(ser, addr, val)
        time.sleep(0.2)

        print(f'Updated ADC clip threshold to {self.ADC_clip_threshold}')

    # Downsample_factor
    def update_Downsample_factor(self):
        # get value
        self.Downsample_factor = int(self.Downsample_factor_entry.get())

        # write vio
        curr_param = next((obj for obj in start_up_params if obj.cmd == 'Downsample_factor'), None)
        addr, val, ignore = parse_cmd('Downsample_factor', self.Downsample_factor)
        send_to_dut(ser, addr, val)
        time.sleep(0.2)

        print(f'Updated Downsample factor to {self.Downsample_factor}')

    def update_plot(self):
        self.ax.relim()
        self.ax.autoscale_view()
        self.root.update_idletasks()
        # time.sleep(0.01)
        self.canvas.draw()

    def receive_data(self):
        global plot_length
        global emulation_on
        global array_length
        global fsample_ADC
        global transmit_length

        time.sleep(0.2)
        print(f'Start to receive ...')

        while self.window_show:
            if self.count == 1_000_000:
                return

            self.x_range_max = plot_length
            if self.plot_frequency.get():
                self.x_range_max = plot_length / array_length * fsample_ADC / 2
            self.x_range_plot = [x * (self.x_range_max / plot_length) for x in self.x_range]

            # receive sequence via UART
            if not emulation_on:
                reader = ser.read(transmit_length)
                # print(len(reader))
            else:
                reader = generate_byte_array(transmit_length)  # simulate the array

            tik = time.time()

            if not reader:
                continue

            if len(reader) != transmit_length:
                continue
            # print('Received ', len(reader), 'quit_flag == ', self.quit_flag)
            result = np.frombuffer(reader, dtype=dt)

            # unpack
            Q_data = result[0:array_length * bytes_per_number:2]
            I_data = result[1:array_length * bytes_per_number:2]

            self.aggregated_results_I.append(I_data)
            self.aggregated_results_Q.append(Q_data)

            # If we have more than 5 inputs, remove the oldest one
            if len(self.aggregated_results_I) > self.aggregate_size:
                self.aggregated_results_I.pop(0)
                self.aggregated_results_Q.pop(0)

            Q_aggregated = average_arrays(self.aggregated_results_Q)
            I_aggregated = average_arrays(self.aggregated_results_I)

            if self.aggregate.get():
                Q_data = Q_aggregated
                I_data = I_aggregated

            if not self.aggregate.get():
                self.aggregated_results_Q.clear()
                self.aggregated_results_I.clear()

            if self.scale_FS.get():
                Q_data = Q_data / scale
                I_data = I_data / scale

            complex_array = np.add(I_data[0:plot_length:decimation], Q_data[0:plot_length:decimation] * 1j)

            x_factor = self.x_range_max / plot_length
            mag_array = 10 ** (-50) + np.abs(complex_array)
            peak_x_lower_bound = self.x_min
            peak_x_upper_bound = self.x_max
            if self.plot_frequency.get():
                peak_x_lower_bound = int(np.floor(peak_x_lower_bound / x_factor))
                peak_x_upper_bound = int(np.ceil(peak_x_upper_bound / x_factor))

            peak_index = np.argmax(mag_array[peak_x_lower_bound:peak_x_upper_bound])
            # peak_value = np.max(mag_array[peak_x_lower_bound:peak_x_upper_bound])
            peak_value = mag_array[peak_index+peak_x_lower_bound]

            peak_x = peak_index
            if self.plot_frequency.get():
                peak_x = peak_index * x_factor

            peak_mag = 20 * np.log10(10 ** (-60) + peak_value)
            peak_phase = np.angle(complex_array[peak_index+peak_x_lower_bound]) * 180 / np.pi

            # Update value
            self.I_data.set_data(self.x_range_plot, I_data)
            self.Q_data.set_data(self.x_range_plot, Q_data)
            self.Mag.set_data(self.x_range_plot, 20 * np.log10(mag_array))
            self.Phase.set_data(self.x_range_plot, np.angle(complex_array) * 180 / np.pi + 180)
            self.peakpt_dB.set_offsets(np.c_[peak_x+self.x_min, peak_mag])

            self.ax.set_xlabel(f'Frequency (Hz)' if self.plot_frequency.get() else f'Frequency Bin Index')
            self.ax.set_title(f'{self.count}-th frame results I and Q' if not self.var_Peak.get()
        else f'{self.count}-th frame results I and Q, peak at {(peak_x+self.x_min):.3f} '
                                   f'with Mag {peak_mag:.2f}, Phase {peak_phase:.2f}')
            self.ax.set_xlim(self.x_min, self.x_max)
            self.ax.set_ylim(self.y_min, self.y_max)
            self.ax2.set_ylim(self.y2_min, self.y2_max)

            self.update_plot()

            self.count += 1
            # print(self.count)

        print('>> Exiting data receive thread.')

    # for vio param setting
    def run_vio(self):
        global bit_index
        # global aggregate
        # global aggregate_size
        global plot_individual_bits
        time.sleep(1.0)

        # start up
        # for params in start_up_params:
        #     addr, val, ignore = parse_cmd(params.cmd, int(params.default_val))
        #     send_to_dut(ser, addr, val)
        cmd, addr, val = reset_all(rootGUI=self)
        send_to_dut(ser, addr, val)

        while not self.quit_flag:
            task = input(highlight_msg('>> usage:VAR_NAME VAL, or VAR_NAME reset, for example, '
                                       'to write 8192 into TX_Mult_gain, type TX_Mult_gain 8192, or type q to quit\r\n'))
            task = task.split()
            conv_factor = 1
            unit = ''
            if (len(task) == 1 and not (task[0] in ['sweep', 'sweep_m', 'q', 'bits'])) or len(task) == 2:
                if task[0] == 'reset' or task[0] == 'write':
                    if len(task) == 2:
                        if  task[0] == 'reset' and task[1] == 'all':
                            cmd, addr, val = reset_all(rootGUI=self)
                            curr_val = np.array([params.default_val for params in start_up_params])
                            conv_factor = np.array([params.conv_factor for params in start_up_params])
                            unit = np.array([params.unit for params in start_up_params])
                            time.sleep(0.1)
                        elif task[0] == 'write':
                            cmd, addr, val = get_all()
                            curr_val = np.array([params.default_val for params in start_up_params])
                            conv_factor = np.array([params.conv_factor for params in start_up_params])
                            unit = np.array([params.unit for params in start_up_params])
                            time.sleep(0.1)
                else:
                    if task[0] == 'tx_freq' or task[0] == 'TX_DAC_frequency_word':
                        cmd = 'TX_DAC_frequency_word'
                    elif task[0] == 'vm_freq' or task[0] == 'VM_DAC_frequency_word':
                        cmd = 'VM_DAC_frequency_word'
                    elif task[0] == 'tx_phase' or task[0] == 'TX_DAC_initial_phase':
                        cmd = 'TX_DAC_initial_phase'
                    elif task[0] == 'vm_phase' or task[0] == 'VM_DAC_initial_phase':
                        cmd = 'VM_DAC_initial_phase'
                    elif task[0] == 'tx_phase_diff' or task[0] == 'TX_IQ_phase_diff':
                        cmd = 'TX_IQ_phase_diff'
                    elif task[0] == 'vm_phase_diff' or task[0] == 'VM_IQ_phase_diff':
                        cmd = 'VM_IQ_phase_diff'
                    elif task[0] == 'tx_mag' or task[0] == 'TX_Mult_gain':
                        cmd = 'TX_Mult_gain'
                    elif task[0] == 'vm_mag' or task[0] == 'VM_Mult_gain':
                        cmd = 'VM_Mult_gain'
                    elif task[0] == 'tx_mult_en' or task[0] == 'TX_Mult_enable':
                        cmd = 'TX_Mult_enable'
                    elif task[0] == 'vm_mult_en' or task[0] == 'VM_Mult_enable':
                        cmd = 'VM_Mult_enable'
                    else:
                        highlight_msg(f'Error: No such parameter!')
                        continue

                if len(task) == 2:
                    if task[0] == 'aggregate':
                        aggregate_size = int(task[1])
                        print(f'Setting aggregate size to {aggregate_size}')
                        continue
                    elif task[1] == 'reset':
                        curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                        addr, ignore, val = parse_cmd(cmd, curr_param.default_val,rootGUI=self)
                        curr_val = curr_param.curr_val
                        conv_factor = curr_param.conv_factor
                        unit = curr_param.unit
                    elif task[1] != 'all':
                        # set parameter manually
                        curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                        if 'phase' or 'frequency' in curr_param.cmd:
                            val_new = int(np.floor(int(task[1]) / curr_param.conv_factor))
                        else:
                            val_new = int(task[1])
                        addr, val, ignore = parse_cmd(cmd, val_new,rootGUI=self)
                        curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                        curr_val = curr_param.curr_val
                        conv_factor = curr_param.conv_factor
                        unit = curr_param.unit
                    send_to_dut(ser, addr, val)
                else:
                    curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                    if curr_param:
                        curr_val = curr_param.curr_val
                        conv_factor = curr_param.conv_factor
                        unit = curr_param.unit
                equiv_val = curr_val * conv_factor
                try:
                    length = len(curr_val)
                    for i in range(length):
                        msg = f'{cmd[i]} is set to {curr_val[i]}, equivalent to {equiv_val[i]} {unit[i]}'
                        print(highlight_msg(msg))
                except TypeError:
                    msg = f'{cmd} is set to {curr_val}, equivalent to {equiv_val} {unit}'
                    print(highlight_msg(msg))

            elif len(task) == 1 or len(task) == 5:
                if task[0] == 'sweep' or task[0] == 'sweep_m':
                    if len(task) == 1:
                        params = input(
                            '>> Enter <tx/vm_freq/phase/mag> <start value> <step size> <number of steps>\r\n '
                            'for example: tx_freq 1 1 100\r\n')
                        params = params.split()
                    else:
                        params = task[1:5]
                    if len(params) == 4:
                        if params[0] == 'tx_freq':
                            cmd = 'TX_DAC_frequency_word'
                        elif params[0] == 'vm_freq':
                            cmd = 'VM_DAC_frequency_word'
                        elif params[0] == 'tx_phase':
                            cmd = 'TX_DAC_initial_phase'
                        elif params[0] == 'vm_phase':
                            cmd = 'VM_DAC_initial_phase'
                        elif params[0] == 'tx_phase_diff':
                            cmd = 'TX_IQ_phase_diff'
                        elif params[0] == 'vm_phase_diff':
                            cmd = 'VM_IQ_phase_diff'
                        elif params[0] == 'tx_mag':
                            cmd = 'TX_Mult_gain'
                        elif params[0] == 'vm_mag':
                            cmd = 'VM_Mult_gain'
                        elif params[0] == 'tx_mult_en' or params[0] == 'TX_Mult_enable':
                            cmd = 'TX_Mult_enable'
                        elif params[0] == 'vm_mult_en' or params[0] == 'VM_Mult_enable':
                            cmd = 'VM_Mult_enable'
                    else:
                        print(highlight_msg(">> Error: please enter tx/vm_freq/phase/mag"))
                        continue
                    start_val = int(params[1])
                    step_val = int(params[2])
                    num_steps = int(params[3])

                    curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                    if 'phase' or 'frequency' in curr_param.cmd:
                        start_val = int(np.floor(start_val / curr_param.conv_factor))
                        step_val = int(np.floor(step_val / curr_param.conv_factor))

                    curr_val = start_val
                    for i in range(num_steps):

                        addr, val, ignore = parse_cmd(cmd, curr_val,rootGUI=self)
                        send_to_dut(ser, addr, val)

                        curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                        conv_factor = curr_param.conv_factor
                        unit = curr_param.unit

                        equiv_val = curr_val * conv_factor
                        msg = f'{cmd} is set to {curr_val}, equivalent to {equiv_val} {unit}'
                        print(highlight_msg(msg))
                        time.sleep(0.2)
                        curr_val += step_val
                        if (task[0] == 'sweep_m'):
                            cont = input("press enter to step\n")
                            if cont == 'q':
                                break

                elif task[0] == 'q':
                    self.quit_flag = True
                    self.window_show = False

                elif task[0] == 'bits':
                    plot_individual_bits = not plot_individual_bits
                    print(f'Plotting the summed waveform' if not plot_individual_bits else f'Plotting bit {bit_index}')
                    while plot_individual_bits:
                        bit_prompt_ans = input("Which bit to plot? or type q to exit this mode\n")
                        if bit_prompt_ans == '':
                            continue
                        if bit_prompt_ans == 'q':
                            plot_individual_bits = not plot_individual_bits
                            break
                        else:
                            bit_index = int(bit_prompt_ans)
                            print(
                                f'Plotting the summed waveform' if not plot_individual_bits else f'Plotting bit {bit_index}')
                # elif task[0] == 'unit':
                #     display_freq = not display_freq
                #     self.x_min =
                #     print(f'Plot x-axis is bin-index' if not display_freq else f'Plot x-axis is frequency (Hz).')
                # elif task[0] == 'aggregate':
                #     self.aggregate = not self.aggregate
                #     print(f'Plotting raw input from FPGA' if not aggregate else f'Plotting post-aggregate results.')

            else:
                print(highlight_msg(">> Error: usage:VAR_NAME VAL, or VAR_NAME reset"))

        print(">> Exiting vio thread.")
        return

    # prepare data container and empty plot
    def fpga_stream_old(self):

        global bit_index
        global multiply_factor
        global display_freq
        global aggregate
        global aggregate_size
        global plot_individual_bits

        x_range = range(0, plot_length, decimation)
        if plot_on:
            fig, ax = plt.subplots(nrows=3, ncols=1)
            # update the plot
            ax[0].clear()

            ax[0].set_title('Awaiting frame results I and Q')
            x_max = plot_length
            if display_freq:
                x_max = plot_length / array_length * fsample_ADC / 2
            x_range_plot = [x * (x_max / plot_length) for x in x_range]
            ax[0].set_xlim(0, x_max)
            ax[0].set_ylim(-40000 if not self.scale_FS.get() else -40000/self.scale,
                           40000 if not self.scale_FS.get() else 40000/self.scale)

            ax[1].clear()
            ax[1].set_title('Awaiting frame results Mag (dB)')
            ax[1].set_xlim(0, x_max)
            ax[1].set_ylim(-10, 80)

            ax[2].clear()
            ax[2].set_title('Awaiting frame results phase (deg)')
            ax[2].set_xlim(0, x_max)
            ax[2].set_ylim(-200, 200)

            fig.suptitle('Received Data from FPGA with %s output' % ('normalized' if self.scale_FS.get() else 'un-normalized'))
            fig.tight_layout()
            plt.pause(0.0001)  # this line will force plotting all pending plots

        count = 0
        print("starts receiving...")
        tok = time.time()

        line_real, = ax[0].plot(x_range_plot, np.linspace(0, 0, len(x_range)), label='FFT_out_real')
        line_imag, = ax[0].plot(x_range_plot, np.linspace(0, 0, len(x_range)), label='FFT_out_imag')

        line_dB, = ax[1].plot(x_range_plot, np.linspace(0, 0, len(x_range)))  # prevent zero
        peakpt_dB = ax[1].scatter([], [], color='r', marker='o')

        line_phase, = ax[2].plot(x_range_plot, np.linspace(0, 0, len(x_range)))
        peakpt_phase = ax[2].scatter([], [], color='r', marker='o')

        aggregated_results_I = []
        aggregated_results_Q = []
        while not self.quit_flag:

            if count == 10500:
                break

            x_max = plot_length
            if display_freq:
                x_max = plot_length / array_length * fsample_ADC / 2
            x_range_plot = [x * (x_max / plot_length) for x in x_range]
            # receive sequence via UART
            if not emulation_on:
                reader = ser.read(transmit_length)
                # print(len(reader))
            else:
                reader = generate_byte_array(transmit_length)  # simulate the array

            tik = time.time()

            if not reader or len(reader) != transmit_length:
                continue

            result = np.frombuffer(reader, dtype=dt)

            # unpack
            Q_data = result[0:array_length * bytes_per_number:2]
            I_data = result[1:array_length * bytes_per_number:2]

            aggregated_results_I.append(I_data)
            aggregated_results_Q.append(Q_data)

            # If we have more than 5 inputs, remove the oldest one
            if len(aggregated_results_I) > aggregate_size:
                aggregated_results_I.pop(0)
                aggregated_results_Q.pop(0)

            Q_aggregated = average_arrays(aggregated_results_Q)
            I_aggregated = average_arrays(aggregated_results_I)

            if aggregate:
                Q_data = Q_aggregated
                I_data = I_aggregated

            if self.scale_FS.get():
                Q_data = Q_data / scale
                I_data = I_data / scale

            complex_array = np.add(I_data[0:plot_length:decimation], Q_data[0:plot_length:decimation] * 1j)

            mag_array = 10 ** (-50) + np.abs(complex_array)
            peak_index = np.argmax(mag_array)
            peak_mag = 20 * np.log10(10 ** (-50) + mag_array[peak_index])
            peak_phase = np.angle(complex_array[peak_index]) * 180 / np.pi

            # update the plot
            if plot_on:
                if not plot_individual_bits:
                    line_real.set_data(x_range_plot, I_data[
                                                     0: plot_length: decimation] if not multiply_factor > 1 else multiply_factor * np.real(
                        complex_array[0: plot_length: decimation]))
                    line_imag.set_data(x_range_plot, Q_data[
                                                     0: plot_length: decimation] if not multiply_factor > 1 else multiply_factor * np.imag(
                        complex_array[0: plot_length: decimation]))
                else:
                    line_real.set_data(x_range_plot, scale * ((I_data[0: plot_length: decimation] >> bit_index) & 1))
                    line_imag.set_data(x_range_plot, scale * ((Q_data[0: plot_length: decimation] >> bit_index) & 1))

                ax[0].set_title(
                    '%d-th frame results I and Q' % count if not plot_individual_bits else f'{bit_index}-th bit from I and Q')
                ax[0].legend(loc='lower center')
                ax[0].set_xlim(0, x_max)
                if self.scale_FS.get():
                    ax[0].set_ylim(-1, 1)
                else:
                    ax[0].set_ylim(-float(scale) * 1.2, float(scale) * 1.2)

                if not plot_individual_bits:
                    line_dB.set_data(x_range_plot, 20 * np.log10(mag_array))
                else:
                    line_dB.set_data(x_range_plot, np.linspace(0, 0, len(x_range)))
                peakpt_dB.set_offsets(np.c_[peak_index, peak_mag])

                ax[1].set_title('%d-th frame results Mag (dB), peak bin mag is %.2f' % (count, peak_mag))
                ax[1].set_xlim(0, x_max)
                if self.scale_FS.get():
                    ax[1].set_ylim(-10 - 20 * np.log10(scale), 100 - 20 * np.log10(scale))
                else:
                    ax[1].set_ylim(-10, 100)

                if not plot_individual_bits:
                    line_phase.set_data(x_range_plot, np.angle(complex_array) * 180 / np.pi)
                else:
                    line_phase.set_data(x_range_plot, np.linspace(0, 0, len(x_range)))

                peakpt_phase.set_offsets(np.c_[peak_index, peak_phase])

                ax[2].set_title('%d-th frame results phase (deg), peak bin phase is %.2f' % (count, peak_phase))
                ax[2].set_xlim(0, x_max)
                ax[2].set_ylim(-200, 200)

                # line_real.set_visible(self.var_I_data.get())
                # line_imag.Q_data.set_visible(self.var_Q_data.get())
                # line_dB.set_visible(self.var_Mag.get())
                # line_phase.set_visible(self.var_Phase.get())

                plt.pause(0.001)
                fig.tight_layout()

            if print_stream_msg:
                print(">> Received %.4d-th frame, peak index is %d, time elapsed is %.4f" % (
                count, peak_index, tik - tok))
            tok = tik
            # if count < 100:
            #     I_received_matrix.append(I_data)
            #     Q_received_matrix.append(Q_data)

            count += 1
        # print(I_received_matrix)
        # print(Q_received_matrix)
        print(">>Done plot")


# Main thread
if __name__ == "__main__":
    # Create threads
    # vio_thread = threading.Thread(target=run_vio)
    # # Start sub thread
    # vio_thread.start()
    root = tk.Tk()
    # root.tk.call('tk', 'scaling', 4.0)
    # root.title("Matplotlib Plot with Tkinter")
    root.winfo_toplevel().title("SenDar Data Spectrum Plot V1.0 by Yikuan Chen")
    root.geometry(f'{w_size}x{h_size}')

    my_app = data_GUI(root)
    root.mainloop()

    # Wait for thread to finish
    # vio_thread.join()
    print('Exiting main...')
    root.destroy()
    exit()
