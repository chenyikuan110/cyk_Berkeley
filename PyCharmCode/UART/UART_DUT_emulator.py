#!/usr/bin/env python3
# modified from eecs151 final project hex_to_serial script
import os
import serial
import numpy as np
import time

##Windows
if os.name == 'nt':
    ser = serial.Serial()
    ser.baudrate = 921600
    ser.port = 'COM8'  # CHANGE THIS COM PORT
    ser.open()
else:
    ser = serial.Serial('/dev/ttyUSB0')
    ser.baudrate = 921600


# for emulation
def generate_byte_array_1024_fft():
    # Initialize an empty byte array
    byte_array = bytearray(1024*2*2)

    I_data = np.zeros(1024)
    for i in range(1000):
        I_data[i] = int(np.sin(((i % 1024) / 40) * (1 + 0.01*np.random.rand())) * 8192 + np.random.rand() * 4)
    FFT_result = np.fft.fft(I_data) / (4 * 4 * 4 * 4 * 8)
    for i in range(1024*2*2):
        index = int(i/4)
        if i % 4 == 0:
            byte_array[i] = (int(np.imag(FFT_result[index])) & 0xFF00) >> 8  # IM_MSB
        elif i % 4 == 1:
            byte_array[i] = int(np.imag(FFT_result[index])) & 0x00FF  # IM_LSB
        elif i % 4 == 2:
            byte_array[i] = (int(np.real(FFT_result[index])) & 0xFF00) >> 8  # RE_MSB
        elif i % 4 == 3:
            byte_array[i] = int(np.real(FFT_result[index])) & 0x00FF  # RE_LSB
    return byte_array


def generate_byte_array(size):
    # Initialize an empty byte array
    byte_array = bytearray(size)

    # Fill odd entries with increasing numbers
    for i in range(size):
        if i % 2 == 1:
            byte_array[i] = 0  # Even entry (filled with zeros)
        else:
            if i % 4 == 0:
                byte_array[i] = int(np.sin(i / 40) * 64 + np.random.rand() * 4) % 256  # I-channel
            else:
                byte_array[i] = int(np.sin((i-2) / 40 - np.pi/2) * 64 + np.random.rand() * 4) % 256  # Q-channel
            # byte_array[i] = int(np.random.rand() * 256) % 256  # Odd entry (increasing number)
            # byte_array[i] = int(i) % 256  # Odd entry (increasing number)

    return byte_array


array_length = 512
bytes_per_number = 2
num_channels = 2
transmit_length = array_length * bytes_per_number * num_channels
count = 0
while True:
    if count % 20 == 0:
        # break
        task = input('>> Press enter to send frame %d to %d' % (count, count+19))
    # byte_array = generate_byte_array(transmit_length)
    byte_array = generate_byte_array_1024_fft()
    ser.write(byte_array[0:transmit_length])
    time.sleep(0.01)
    count += 1

exit()