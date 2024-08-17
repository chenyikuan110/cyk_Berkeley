#!/usr/bin/env python3
import os
import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import threading


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
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM9'  # CHANGE THIS COM PORT
    ser.timeout = 2
    ser.open()
else:
    ser = serial.Serial('/dev/ttys002')
    ser.baudrate = 115200  # 921600

# emulation enable
emulation_on = False
emulation_fft = False
plot_individual_bits = False
bit_index = 0
plot_on = True
scale_FS = False
print_stream_msg = False
scale = 1 << 15
decimation = 1

# Prepare serial read parameters
LUT_size = 32768
array_length = 512
bytes_per_number = 2
num_channels = 2
transmit_length = array_length * bytes_per_number * num_channels
plot_length = array_length

fsample = 80E6
fund_tone = fsample / 4 / LUT_size

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
I_received_matrix = []
Q_received_matrix = []
# input("Open a serial program in another terminal, then hit Enter")


# this flag kills both threads
quit_flag = 0


# print with color utility
def highlight_msg(msg):
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
    return byte_array #[::-1] # because I flipped the endianess in verilog


# for command to addr conversion
def parse_cmd(cmd, val):
    curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)

    start_addr = curr_param.addr
    width = curr_param.width
    default_val = curr_param.default_val
    address = [n for n in reversed(range(start_addr, start_addr + width))]
    curr_param.curr_val = val
    # print(cmd, val, address, int_to_bytes(val, width))

    return address, int_to_bytes(val, width), int_to_bytes(default_val, width)


# reset value
def reset_all():
    addr = []
    val = []
    cmds = []
    # for cmd_keys, cmd_vals in dict_cmd.items():
    for params in start_up_params:
        addr_, ignore, val_ = parse_cmd(params.cmd, params.default_val)
        addr.append(addr_)
        val.append(val_)
        cmds.append(params.cmd)
    return cmds, np.concatenate(addr), np.concatenate(val)


# send msg
def send_to_dut(port, addr, val):
    for i in reversed(range(len(addr))):
        msg = '[sending] ' + str(val[i]) + ' to address ' \
              + str(addr[i]) + ': ' + str(49) + ' ' + str(addr[i]) + ' ' + str(val[i])
        print(highlight_msg(msg))
        port.write(bytearray([49, addr[i], val[i]]))
        time.sleep(0.01)


# for vio param setting
def run_vio():
    global quit_flag
    global bit_index
    time.sleep(1.0)

    # start up
    # for params in start_up_params:
    #     addr, val, ignore = parse_cmd(params.cmd, int(params.default_val))
    #     send_to_dut(ser, addr, val)
    cmd, addr, val = reset_all()
    send_to_dut(ser, addr, val)

    while quit_flag == 0:
        task = input(highlight_msg('>> usage:VAR_NAME VAL, or VAR_NAME reset, for example, '
                                   'to write 8192 into TX_Mult_gain, type TX_Mult_gain 8192, or type q to quit\r\n'))
        task = task.split()
        conv_factor = 1
        unit = ''
        if (len(task) == 1 and not (task[0] in ['sweep', 'sweep_m', 'q'])) or len(task) == 2:
            if task[0] == 'reset':
                if len(task) == 2:
                    if task[1] == 'all':
                        cmd, addr, val = reset_all()
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
                if task[1] == 'reset':
                    curr_param = next((obj for obj in start_up_params if obj.cmd == cmd), None)
                    addr, ignore, val = parse_cmd(cmd, curr_param.default_val)
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
                    addr, val, ignore = parse_cmd(cmd, val_new)
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
                    params = input('>> Enter <tx/vm_freq/phase/mag> <start value> <step size> <number of steps>\r\n '
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

                    addr, val, ignore = parse_cmd(cmd, curr_val)
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
                quit_flag = 1
            elif task[0] == 'bits':
                plot_individual_bits = not plot_individual_bits
                print(f'Plotting the summed waveform' if not plot_individual_bits else f'Plotting bit {bit_index}')
                while plot_individual_bits:
                    bit_prompt_ans = input("which bit to plot?")
                    if bit_prompt_ans == 'q':
                        break
                    else:
                        bit_index = int(bit_prompt_ans)

        else:
            print(highlight_msg(">> Error: usage:VAR_NAME VAL, or VAR_NAME reset"))

    print(">>Done vio")


# for emulation
def generate_byte_array(size):
    # Initialize an empty byte array
    print_stream_msg: \
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


# prepare data container and empty plot
def fpga_stream():
    global quit_flag
    x_range = range(0, plot_length, decimation)
    if plot_on:
        fig, ax = plt.subplots(nrows=3, ncols=1)
        # update the plot
        ax[0].clear()

        ax[0].set_title('Awaiting frame results I and Q')
        ax[0].set_xlim(0, plot_length)
        ax[0].set_ylim(-40000, 40000)

        ax[1].clear()
        ax[1].set_title('Awaiting frame results Mag (dB)')
        ax[1].set_xlim(0, plot_length)
        ax[1].set_ylim(-10, 80)

        ax[2].clear()
        ax[2].set_title('Awaiting frame results phase (deg)')
        ax[2].set_xlim(0, plot_length)
        ax[2].set_ylim(-200, 200)

        fig.suptitle('Received Data from FPGA with %s output' % ('normalized' if scale_FS else 'un-normalized'))
        fig.tight_layout()
        plt.pause(0.0001)

    count = 0
    print("starts receiving...")
    tok = time.time()

    line_real, = ax[0].plot(x_range, np.linspace(0,0,len(x_range)), label='FFT_out_real')
    line_imag, = ax[0].plot(x_range, np.linspace(0,0,len(x_range)), label='FFT_out_imag')

    line_dB, = ax[1].plot(x_range, np.linspace(0,0,len(x_range)))  # prevent zero
    peakpt_dB = ax[1].scatter([], [], color='r', marker='o')

    line_phase, = ax[2].plot(x_range, np.linspace(0,0,len(x_range)))
    peakpt_phase = ax[2].scatter([], [], color='r', marker='o')

    while quit_flag != 1:
        if count == 10500:
            break

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

        if scale_FS:
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
                line_real.set_data(x_range, I_data[0: plot_length: decimation])
                line_imag.set_data(x_range, Q_data[0: plot_length: decimation])
            else:
                line_real.set_data(x_range, (I_data[0: plot_length: decimation] >> bit_index) & 1)
                line_imag.set_data(x_range, (Q_data[0: plot_length: decimation] >> bit_index) & 1)

            ax[0].set_title('%d-th frame results I and Q' % count)
            ax[0].legend(loc='lower center')
            ax[0].set_xlim(0, plot_length)
            if scale_FS:
                ax[0].set_ylim(-1, 1)
            else:
                ax[0].set_ylim(scale * 1.2, -scale * 1.2)

            if not plot_individual_bits:
                line_dB.set_data(x_range, 20 * np.log10(mag_array))
            else:
                line_dB.set_data(x_range, np.linspace(0,0,len(x_range)))
            peakpt_dB.set_offsets(np.c_[peak_index, peak_mag])

            ax[1].set_title('%d-th frame results Mag (dB), peak bin mag is %.2f' % (count, peak_mag))
            ax[1].set_xlim(0, plot_length)
            if scale_FS:
                ax[1].set_ylim(-10 - 20 * np.log10(scale), 90 - 20 * np.log10(scale))
            else:
                ax[1].set_ylim(-10, 90)

            if not plot_individual_bits:
                line_phase.set_data(x_range, np.angle(complex_array) * 180 / np.pi)
            else:
                line_dB.set_data(x_range, np.linspace(0,0,len(x_range)))

            peakpt_phase.set_offsets(np.c_[peak_index, peak_phase])

            ax[2].set_title('%d-th frame results phase (deg), peak bin phase is %.2f' % (count, peak_phase))
            ax[2].set_xlim(0, plot_length)
            ax[2].set_ylim(-200, 200)

            plt.pause(0.001)
            fig.tight_layout()

        if print_stream_msg:
            print(">> Received %.4d-th frame, peak index is %d, time elapsed is %.4f" % (count, peak_index, tik - tok))
        tok = tik
        if count < 100:
            I_received_matrix.append(I_data)
            Q_received_matrix.append(Q_data)

        count += 1
    # print(I_received_matrix)
    # print(Q_received_matrix)
    print(">>Done plot")


# Main thread
if __name__ == "__main__":
    # Create threads
    vio_thread = threading.Thread(target=run_vio)
    # Start sub thread
    vio_thread.start()
    fpga_stream()

    # Wait for thread to finish
    vio_thread.join()
    exit()
