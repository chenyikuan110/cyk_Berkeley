import os
import math
import sys
import time
import csv
import numpy as np
import matplotlib.pyplot as plt

oscilloscope_mode = True

LUT_size = 16384
LUT_addr_bitwidth = int(np.log2(LUT_size))
array_length = 1/152.6 #16384e-6  # seconds
init_phase = np.pi - 1
fsample = 100_000_000  # 1/fsample is 100 ns
fBW = 10_000_000_000  # 10 GHz
Tchirp = 100e-6
array_length_sample = int(array_length * fsample)
ftone = 10_000#10_000

fundamental_tone = fsample / 4 / LUT_size
t_tuning = (fundamental_tone/fBW)*Tchirp

freq_step = int(ftone / fundamental_tone)
harmonic_num = int(ftone / fundamental_tone)
harmonic_approx = harmonic_num * fundamental_tone
print("Sampling Frequency is %d with LUT-size = %d" % (fsample, LUT_size))
print("Fundamental tone is %.2f Hz, this corresponds to t_tuning of %.2f ps" % (fundamental_tone, t_tuning*1e12))
print("Required Freq: %.2f Hz, nearest tone producable is %d * %.2f = %.2f Hz" % (
ftone, harmonic_num, fundamental_tone, harmonic_approx))
print("Output array length will be %d samples with frequency step of %d " % (array_length_sample, freq_step))

LUT_path = 'sine_0to90_16384_16b.mem'


# phase-to-index mapping block to get initial phase, this block will not appear in verilog
def phase_to_index(phase):
    global LUT_size
    index = int(phase / (np.pi / 2) * LUT_size) % int(4 * LUT_size)
    return index


# formatting helper
def human_format(num):
    num = float('{:.3f}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:.3f}'.format(num).rstrip('0').rstrip('.'), ['', 'k', 'M', 'B', 'T'][magnitude])


# load the LUT
LUT = np.zeros(LUT_size)
with open(LUT_path, "r") as file:
    for i, line in enumerate(list(file)):
        LUT[i] = int(line, 2)

# plt.plot(LUT)
# plt.show()
# initialize the output array
fig, ax = plt.subplots(nrows=1, ncols=1)
ftone_new = ftone
curr_phase = init_phase
for i in range(1000):

    harmonic_num = int(ftone_new / fundamental_tone)
    harmonic_approx = harmonic_num * fundamental_tone
    index_step = int(ftone_new / fundamental_tone)

    DAC_out = np.zeros(array_length_sample)

    # mimic the phase accumulator
    phase_step = index_step * (fundamental_tone / fsample * 2 * np.pi)
    phase_accum = phase_to_index(curr_phase)
    # print("Initial Phase is %.2f (phase accum = %d)" % (init_phase, phase_accum))

    for count in range(array_length_sample):
        quadrant = int(phase_accum & (0x3 << LUT_addr_bitwidth)) >> LUT_addr_bitwidth  # detect bits
        sign = int(quadrant >> 1)
        odd_quadrant = int(quadrant & 1)
        index = int(phase_accum & ((1 << LUT_addr_bitwidth) - 1))
        truncated_index = index if odd_quadrant == 0 else ((1 << (LUT_addr_bitwidth + 1)) - 1 - index) & (
                    (1 << LUT_addr_bitwidth) - 1)  # get the LSBs
        value = LUT[truncated_index]
        DAC_out[count] = value if sign == 0 else 2 ** 16 - value
        # print(phase_accum, quadrant, index, truncated_index, value, DAC_out[count])
        phase_accum = (phase_accum + index_step) % int(LUT_size * 4)  # add two more bits to phase accumulator

    # emulate unsigned to signed conversion
    for count in range(array_length_sample):
        DAC_out[count] = DAC_out[count] if DAC_out[count] < 32768 else DAC_out[count] - 2 ** 16

    ax.clear()
    ax.plot(DAC_out)
    ax.set_xlim(0, array_length_sample)
    ax.set_ylim(-34000, 34000)
    if oscilloscope_mode:
        ax.set_title("DAC output array with frequency = %sHz \n, initial phase = %.2f deg, and current phase = %.2f deg"
                     % (human_format(harmonic_approx), init_phase * 180 / np.pi, curr_phase * 180 / np.pi))
    else:
        ax.set_title("DAC output array with frequency = %sHz \n and initial phase = %.2f deg"
                     % (human_format(harmonic_approx), init_phase * 180 / np.pi))
    plt.pause(0.05)

    # init_phase += 0.1
    if oscilloscope_mode:
        curr_phase += phase_step
    else:
        ftone_new += fundamental_tone
