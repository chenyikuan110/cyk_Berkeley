import os
import math
import sys
import time
import csv
import numpy as np
import matplotlib.pyplot as plt
# size = 10240
#
# array = np.zeros(size)
# for i in range(0, size):
    # print("scan_data["+str(i)+"] <= 1'b0;")
    # num = int(np.sin(2* np.pi* i/ size/4) * 32768 + 0*np.random.rand() * 4)
    # num = int(np.sin(((i % 1024) / 40) * (1 + 0.01 * np.random.rand())) * 8192 + np.random.rand() * 4)
    # if num < 0:
    #     num = 2**16+num
    # bits_string = '{:0{width}b}'.format(num, width=16)
    # print(bits_string)
    # array[i] = num

def print_twos_complement(val, bits):
    """Print the two's complement of an integer value."""
    if val < 0:
        val = (1 << bits) + val
    format_string = '{:0' + str(bits) + 'b}'
    return format_string.format(val)

freq = 40E3
npoint = 32768
t = np.linspace(0,1/freq/4,npoint)
array = []
for i in range(0,npoint):
    # string = int(np.floor((2**15-1)*np.sin(2*np.pi*freq*t[i])))
    string = int(np.floor((2 ** 15 - 1) * np.sin(2 * np.pi * freq * t[i])))
    array.append(string)
    bits = print_twos_complement(string,16)
    print(bits)
plt.figure()
plt.plot(array)
plt.show()