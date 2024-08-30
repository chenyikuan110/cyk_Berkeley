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
#
# def print_twos_complement(val, bits):
#     """Print the two's complement of an integer value."""
#     if val < 0:
#         val = (1 << bits) + val
#     format_string = '{:0' + str(bits) + 'b}'
#     return format_string.format(val)
#
# freq = 40E3
# npoint = 32768
# t = np.linspace(0,1/freq/4,npoint)
# array = []
# for i in range(0,npoint):
#     # string = int(np.floor((2**15-1)*np.sin(2*np.pi*freq*t[i])))
#     string = int(np.floor((2 ** 15 - 1) * np.sin(2 * np.pi * freq * t[i])))
#     array.append(string)
#     bits = print_twos_complement(string,16)
#     print(bits)
# plt.figure()
# plt.plot(array)
# plt.show()
array = []
offset = 42
for i in range(0,20):
    array.append(i & 0xC000 + ((i & 0x1FFF) << 1))
    # print(i, '{:0{width}b}'.format(i, width=16))
    # print(f'8\'d{i*2+offset}: begin VM_gain_seq_{i}_reg_1 <= val_to_write; end')
    # print(f'8\'d{i*2+offset+1}: begin VM_gain_seq_{i}_reg_0 <= val_to_write; end')
    # print(f'VM_gain_seq_{i}_reg_1 <= 8\'hFF;')
    # print(f'VM_gain_seq_{i}_reg_0 <= 8\'hFF;')
    # print(f'reg [7:0] VM_gain_seq_{i}_reg_1, VM_gain_seq_{i}_reg_0;')
    # # print(f'assign VM_gain_seq[{i}] =','{',f'VM_gain_seq_{i}_reg_1, VM_gain_seq_{i}_reg_0','};')
    # print(f'assign VM_gain_seq[{i}] =', '{', f'VM_gain_seq_{i}_reg_1, VM_gain_seq_{i}_reg_0', '};')

print('')
offset = offset + i*2 + 2
for i in range(0,20):
    # array.append(i & 0xC000 + ((i & 0x1FFF) << 1))
    # print(i, '{:0{width}b}'.format(i, width=16))
    # print(f'8\'d{i*2+offset}: begin VM_phase_seq_{i}_reg_1 <= val_to_write; end')
    # print(f'8\'d{i*2+offset+1}: begin VM_phase_seq_{i}_reg_0 <= val_to_write; end')
    # print(f'VM_phase_seq_{i}_reg_1 <= 8\'h00;')
    # print(f'VM_phase_seq_{i}_reg_0 <= 8\'h00;')
    # print(f'reg [7:0] VM_phase_seq_{i}_reg_1, VM_phase_seq_{i}_reg_0;')
    # print(f'assign VM_phase_seq[{i}] =', '{', f'VM_phase_seq_{i}_reg_1, VM_phase_seq_{i}_reg_0', '};')
    print(f'{i},{0xFFFF},{0}')

# plt.plot(array)
# plt.show()