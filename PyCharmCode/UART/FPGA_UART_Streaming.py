#!/usr/bin/env python3
# modified from eecs151 final project hex_to_serial script
import os
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import sys
import time
import csv


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


# Windows
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM6'  # CHANGE THIS COM PORT
    ser.open()
else:
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 115200  # 921600


# emulation enable
emulation_on = True
emulation_fft = False
plot_on = True
scale_FS = True
scale = 1 << 15
decimation = 1

# Prepare serial read parameters
array_length = 512
bytes_per_number = 2
num_channels = 2
transmit_length = array_length * bytes_per_number * num_channels
plot_length = array_length

# Prepare byte-to-integer conversion
dt = np.dtype(np.int16)
dt = dt.newbyteorder('>')

# input("Open a serial program in another terminal, then hit Enter")
I_received_matrix = []
Q_received_matrix = []

# for emulation
def generate_byte_array(size):
    # Initialize an empty byte array
    print('Generating bytes')
    byte_array = bytearray(size)

    data = np.zeros(int(size / 2))
    for i in range(int(size / 2)):
        data[i] = int(np.sin(((i % 1024) / 80) * (1 + 0.01 * np.random.rand())) * 8192 + np.random.rand() * 0)

    global emulation_fft
    if emulation_fft:
        data = np.fft.fft(data)/(4*4*4*4*4)

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
while True:
    if count == 10500:
        break

    # receive sequence via UART
    if not emulation_on:
        reader = ser.read(transmit_length)
    else:
        reader = generate_byte_array(transmit_length)  # simulate the array
    # time.sleep(0.025)
    # if count % 8 > 0:
    #     count += 1
    #     continue
    tik = time.time()

    result = np.frombuffer(reader, dtype=dt)
    # for i in range(transmit_length):
    #     bits_string = '{:0{width}b}'.format(reader[i], width=8)
    #     # print(i, bits_string, hex(reader[i]))
    #     print(bits_string)
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
        x_range = range(0, plot_length, decimation)
        ax[0].clear()
        ax[0].plot(x_range, I_data[0:plot_length:decimation], label='FFT_out_real')
        ax[0].plot(x_range, Q_data[0:plot_length:decimation], label='FFT_out_imag')
        ax[0].set_title('%d-th frame results I and Q' % count)
        ax[0].legend(loc='lower center')
        ax[0].set_xlim(0, plot_length)
        if scale_FS:
            ax[0].set_ylim(-1, 1)
        else:
            ax[0].set_ylim(scale * 1.2, -scale * 1.2)

        ax[1].clear()
        ax[1].plot(x_range, 20 * np.log10(mag_array))  # prevent zero
        ax[1].scatter(peak_index, peak_mag, color='r', marker='o')
        ax[1].set_title('%d-th frame results Mag (dB), peak bin mag is %.2f' % (count, peak_mag))
        ax[1].set_xlim(0, plot_length)
        if scale_FS:
            ax[1].set_ylim(-10-20*np.log10(scale), 90-20*np.log10(scale))
        else:
            ax[1].set_ylim(-10, 90)

        ax[2].clear()
        ax[2].plot(x_range, np.angle(complex_array)*180/np.pi)
        ax[2].scatter(peak_index, peak_phase, color='r', marker='o')
        ax[2].set_title('%d-th frame results phase (deg), peak bin phase is %.2f' % (count, peak_phase))
        ax[2].set_xlim(0, plot_length)
        ax[2].set_ylim(-200, 200)

        plt.pause(0.001)
        fig.tight_layout()
    print(">> Received %.4d-th frame, peak index is %d, time elapsed is %.4f" % (count, peak_index, tik - tok))
    tok = tik
    if count < 100:
        I_received_matrix.append(I_data)
        Q_received_matrix.append(Q_data)

    count += 1
# print(I_received_matrix)
# print(Q_received_matrix)
print(">>Done")
