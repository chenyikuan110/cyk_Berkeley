# .coe Xilinx memory file generator
# By: Yikuan Chen
#     2021, Oct
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import numpy as np
import os
import matplotlib.pyplot as pyplot
import csv


def sine_test_pattern(length, freq, timestep, relative_amp, nbits, phase_offset_deg, quantization_mode):
    y = np.zeros(length)
    phase_offset = phase_offset_deg / 180 * np.pi
    for i in range(length):
        # number range [0,1]
        y[i] = relative_amp / 2 * np.sin(2 * np.pi * freq * timestep * i - phase_offset) + 0.5
    # quantize to n-bit integer
    if quantization_mode == "truncate":
        y = np.floor(y * 0.9999999999 * (2 ** nbits))  # to prevent overflow
    else:
        y = np.round(y * (2 ** nbits - 1))
    return y.astype(int)


def int2bin(num, nbits):
    b = np.zeros(nbits)
    if num > 2 ** nbits - 1 or num < 0:
        print(str(num) + " cannot be represented by " + str(nbits) + " binary!")
    else:
        # print(str(num) + ":")
        for i in range(nbits):
            b[i] = num % 2  # TODO:LSB on the leftmost side!!! No need to fix, just a highlight
            num = np.floor(num / 2)
    # print(str(b))
    return b


def intArray_to_binary(array, nbits):
    length = len(array)
    b = np.zeros((length, nbits))
    for i in range(length):
        b[i] = int2bin(array[i], nbits)
    # print(b)
    return b


def zip_I_and_Q(I, Q):
    I_length = len(I)
    Q_length = len(Q)
    length = max(I_length, Q_length)

    I_nbits = len(I[0])
    Q_nbits = len(Q[0])

    nbits = I_nbits + Q_nbits

    y = np.zeros((length, nbits))
    for i in range(length):
        if i < I_length:
            y[i][0:I_nbits] = I[i]
        if i < Q_length:
            y[i][I_nbits:nbits] = Q[i]
        print(y[i])
    print("[" + "I. " * I_nbits + "Q. " * Q_nbits + "]")
    print("LSB<" + "--" * I_nbits + ">MSB LSB<" + "--" * Q_nbits + ">MSB")
    return y


# Unscramble the bits so the bits order matches the PC routing
# this function is needed because Rohit scrambled the bit orders to achieve
# length-matching as much as possible
def unscramble(zipped_data_bits, mapping_list):
    if len(zipped_data_bits) == 0 or len(mapping_list) == 0:
        print("Invalid matrix input!")
        return -1
    if len(zipped_data_bits[0]) != len(mapping_list):
        print("Mapping file is not complete! Please check the file.")
        return -1

    length = len(zipped_data_bits)  # this is data length aka how many time-samples
    width = len(mapping_list)
    y = np.zeros((length, width))
    # y = np.transpose(y)
    # zipped_data_bits_tp = np.transpose(zipped_data_bits)

    order_list = np.zeros((width, 1))  # print the order list for sanity check

    for i in range(width):
        index = int(mapping_list[i][3])
        if mapping_list[i][2] == 'Q':
            index = index + 10
        if mapping_list[i][1] == 'P':
            y[:, i] = zipped_data_bits[:, int(index)]
        else:
            # if 'N', need to flip the bit
            y[:, i] = np.ones((1, length)) - zipped_data_bits[:, int(index)]
        # print(i,index)
        order_list[i] = index if (mapping_list[i][1] == 'P') else -index
    print('(unscramble method 1) The new order of bits is:\n', np.transpose(order_list))
    # y = np.transpose(y)
    return y


# de-scramble based on a different file created on Dec 28, 2023
# input is iq-zipped (bit concatenated) arrays, #row=#timesample, #col = #ibits+#qbits
# output is column swapped version of the input bit, nth col should correspond to the
# actual bit-index this nth channel is routed to on PCB
def unscramble2(zipped_data_bits, mapping_list, num_bits):
    if len(zipped_data_bits) == 0 or num_bits == 0:
        print("Invalid matrix input!")
        return -1
    if len(zipped_data_bits[0]) != num_bits:
        print("Mapping file is not complete! Please check the file.")
        return -1

    length = len(zipped_data_bits)  # this is data length aka how many time-samples
    width = num_bits # for midas, it should be 20
    y = np.zeros((length, width))

    order_list = np.zeros((width, 1))  # print the target bit-index from 0-th channel to max channel for sanity check
    print("starts to swap cols (method 2) to match with PCB routing...")
    for i in reversed(range(width)):
        channel_index = int(mapping_list[2 + i * 16][2]) # find which channel i-th iteration should fill
        target_bit_index = int(mapping_list[2 + i * 16][10]) # find which bit
        is_I_or_Q = mapping_list[2 + i * 16][8]
        is_P_or_N = mapping_list[2 + i * 16][11]
        if is_I_or_Q == 'Q':
            target_bit_index = target_bit_index + 10
        if is_P_or_N == 'P':
            y[:, channel_index] = zipped_data_bits[:, int(target_bit_index)]
        else:
            # if 'N', need to flip the bit
            y[:, channel_index] = np.ones((1, length)) - zipped_data_bits[:, int(target_bit_index)]
        # print(i,index)
        order_list[channel_index] = target_bit_index if (is_P_or_N == 'P') else -target_bit_index
        print(str(channel_index) +','+ is_P_or_N +','+ is_I_or_Q+',' + str(target_bit_index-(10 if is_I_or_Q == 'Q' else 0)))
    print('(unscramble method 2) The new order of bits is:\n', np.transpose(order_list))
    # y = np.transpose(y)
    return y


# bram stores bits in the following format:
# I[0][serdes_bitwidth-1:0], I[1][serdes_bitwidth-1:0] ...
def binary_to_bram(b, bram_data_width, serdes_data_width):
    array_length = len(b)
    nbits = 0
    if len(b):
        if len(b[0]):
            nbits = len(b[0])
    print("test sequence length = " + str(array_length))
    if nbits == 0:
        print("Error with input array")
        return

    # begin real code
    num_taps = int(serdes_data_width / 2)  # for MIDAS, it's 16, since it updates once per clock up-down tick
    bram_max_addr = int(np.ceil(array_length / num_taps))
    print("bram_max_addr:" + str(bram_max_addr))
    print("num_taps per output:" + str(num_taps))
    print("nbits I+Q zipped:" + str(nbits))
    output_matrix = np.zeros((bram_max_addr, bram_data_width))

    for i in range(bram_max_addr):
        for j in range(nbits):
            for k in range(num_taps):
                # if sequence length < max_address * num_taps_per_address
                # the rest of the bits will be set to 0
                if i * num_taps + k < array_length:
                    output_matrix[i][j * num_taps + k] = b[i * num_taps + k][j]

    return output_matrix, bram_max_addr


# turn a 0,1 matrix into binary or hex string
# string_type can be 'bin' or 'hex'
def bin_to_string(matrix, string_type='bin', prefix=''):
    if len(matrix) == 0:
        print("Invalid matrix input!")
        return -1
    matrix_height = len(matrix)
    line_width = len(matrix[0])

    # pad the matrix so each line has 4*N bits
    if line_width % 4 != 0:
        matrix = np.hstack((matrix, np.zeros((matrix_height, 4 - line_width % 4))))
        line_width = len(matrix[0])

    matrix = matrix.astype(int)
    num_hex_digits = int(line_width / 4)

    output = []

    for i in range(matrix_height):
        reversed_bit_array = matrix[i][::-1]  # put LSB on rightmost side
        binary_string = ''.join(map(str, reversed_bit_array))  # turn array into string
        if string_type == 'hex':
            hex_val = '%.*x' % (num_hex_digits, int('0b' + binary_string, 0))
            hex_val = prefix + hex_val
            output.append(hex_val)
        else:
            output.append(binary_string)

    return output


# write our matrix to Xilinx .coe memory file
# radix can be 16 or 2
def write_to_coe(string, radix, output_file_path, output_file_name):
    full_file_path = os.path.join(output_file_path, output_file_name)

    # create results folder path & config file if it does not exist
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    fp = open(full_file_path, 'w')
    # headers
    fp.write(";This .coe file is generated by third party script\n")
    fp.write(";script written by Yikuan Chen in Oct 2021\n")
    fp.write(";for the purpose of MIDAS Tx test only\n")
    fp.write("memory_initialization_radix=" + str(radix) + ";\n")
    fp.write("memory_initialization_vector=")

    for line in string[:-1]:
        fp.write("{},\n".format(line))
    fp.write("{};".format(string[-1]))

    fp.close()

    return


#########################
# Main below
#########################
fOS = 5e9  # for MIDAS it's 5 GHz
fIF = 0.5e9  # for MIDAS it's 250 MHz, 500MHz or 1Ghz
nbits = 10  # for MIDAS it's 10
round_mode = "round"  # round or truncate
relative_amp = 1  # 0 < relative_amp <= 1
timestep = 1 / fOS

sequence_length = 128  # number of samples,
serdes_data_width = 32  # for MIDAS it's 32
bram_data_width = int(2 ** (np.ceil(np.log2(serdes_data_width / 2 * nbits * 2))))
# bram_data_width = 512  # for MIDAS it's 512 = 2^(ceil(logbase2(serdes_data_width / 2 *nbits * 2)))

# coe file related
bool_unscramble = True
output_file_path = '.\COE'
additional_info = '_2023Dec29_unscrambled_IQ_sinusoidal_'
output_file_name = 'test_vector_dacWidth' + str(nbits) + '_serdesWidth' + str(
    serdes_data_width) + additional_info + '.coe'

# run code

time = np.linspace(0, timestep * sequence_length, sequence_length)

# use this to generate a sine wave
I_data = sine_test_pattern(sequence_length, fIF, timestep, relative_amp, nbits, phase_offset_deg=0, quantization_mode=round_mode)
Q_data = sine_test_pattern(sequence_length, fIF, timestep, relative_amp*0.8, nbits, phase_offset_deg=30, quantization_mode=round_mode)

# use the following lines to generate random bits
# I_data = np.floor(np.random.rand(128) * 1023)
# Q_data = np.zeros(128)

I_data_bits = intArray_to_binary(I_data, nbits)
Q_data_bits = intArray_to_binary(Q_data, nbits)

zipped_data_bits = zip_I_and_Q(I_data_bits, Q_data_bits)

# unscramble the matrix to fit the actual bit routing on PCB
fp_mapping_list = open('.\mapping_list.csv', 'r')
mapping_list = list(csv.reader(fp_mapping_list, delimiter=","))
print(zipped_data_bits[:, 0])
unscrambled_matrix = unscramble(zipped_data_bits, mapping_list)
print(unscrambled_matrix)
print(unscrambled_matrix[:, 0])

# unscramble with a different method
fp_mapping_list2 = open('.\mappling_list2.csv', 'r')
mapping_list2 = list(csv.reader(fp_mapping_list2, delimiter=","))
unscrambled_matrix2 = unscramble2(zipped_data_bits, mapping_list2, nbits * 2)
print("unscramble 2")
print(unscrambled_matrix2)
print(unscrambled_matrix2[:, 4])

# print the zipped and unscrambled data
print("\n\nserdes_data_width per lane:" + str(int(serdes_data_width)) + " (serial output @ " + str(fOS / 1e9) + "GHz)")
print("requested # of taps per lane:" + str(int(serdes_data_width / 2)) + " (loaded @ " + str(
    fOS / (serdes_data_width / 2) / 1e9) + "GHz)")
print("bram_data_width:" + str(bram_data_width) +
      "(> serdes_data_width/2*nbits*2 = "
      + str(serdes_data_width) + "*" + str(nbits) + " = " + str(serdes_data_width * nbits) + ")")

if bool_unscramble:
    print("\noutput bit to be stored in bram is unscrambled:")
    output_matrix, bram_max_addr = binary_to_bram(unscrambled_matrix2, bram_data_width, serdes_data_width)
else:
    print("\noutput bit to be stored in bram is NOT unscrambled:")
    output_matrix, bram_max_addr = binary_to_bram(zipped_data_bits, bram_data_width, serdes_data_width)


print(output_matrix)

hex_string = bin_to_string(output_matrix, 'hex', prefix='')
assert len(hex_string) == bram_max_addr

write_to_coe(hex_string, 16, output_file_path, output_file_name)

pyplot.step(time * 1e9, I_data, where="post")
pyplot.plot(time * 1e9, I_data, label="I_data")
pyplot.plot(time * 1e9, Q_data, label="Q_data")
pyplot.legend()
pyplot.xlabel("ns")
pyplot.title("DAC data generation with f_IF=" + str(fIF / 1e6) + " MHz\n"
                                                                 " and f_OS=" + str(fOS / 1e9) + " GHz\n"
                                                                                                 " Max val =" + str(
    max(I_data)) + "\n"
                   " Min val =" + str(min(I_data)) + "\n"
                                                     " Quantization level = " + str(nbits) + " bits")
pyplot.tight_layout()
pyplot.show()
