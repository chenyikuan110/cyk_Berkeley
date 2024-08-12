import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from pylab import *
import os
import glob
from scipy.interpolate import interp1d
import csv

plt.rcParams['axes.unicode_minus'] = False
# Initialization
debug = 1
d = 0.32
freq_min = 120
freq_max = 150

my_dir = ""
my_subdir = ""
atten_value = "atten_1.00"

# Load reference power data
file = f'{my_dir}{my_subdir}extender_power.xlsx'
tmp = pd.read_excel(file).values.T
freq_ref_power_course = tmp[0, :]
ref_power_course = tmp[1, :]

# Load OE gain data
file = f'{my_dir}{my_subdir}OE_gain.csv'
tmp = pd.read_csv(file).values.T
freq_oe_gain = tmp[0, :]
oe_gain_smooth = tmp[1, :]
oe_gain_actual = tmp[2, :]

# Load horn gain data
file = f'{my_dir}{my_subdir}horn_gain.csv'
tmp = pd.read_csv(file).values.T
freq_horn_gain = tmp[0, :]
horn_gain_smooth = tmp[1, :]
horn_gain_actual = tmp[2, :]

# Load attenuation data
my_subdir = "Atten\\"
file = f'{my_dir}{my_subdir}{atten_value}.csv'
tmp = pd.read_csv(file).values.T
freq_atten10 = tmp[0, :] / 1e9
atten10 = tmp[1, :]

atten_value = "atten_1.20"
file = f'{my_dir}{my_subdir}{atten_value}.csv'
tmp = pd.read_csv(file).values.T
freq_atten12 = tmp[0, :] / 1e9
atten12 = tmp[1, :]

atten_value = "atten_1.40"
file = f'{my_dir}{my_subdir}{atten_value}.csv'
tmp = pd.read_csv(file).values.T
freq_atten14 = tmp[0, :] / 1e9
atten14 = tmp[1, :]

# Define frequency range and interpolate data
freq = np.arange(freq_min, freq_max, 0.25)
fspl = -20 * np.log10(d * freq * 10 * 4 * np.pi / 3)

interp_ref_power = interp1d(freq_ref_power_course, ref_power_course, kind='cubic', fill_value="extrapolate")
ref_power = interp_ref_power(freq)

interp_oe_gain = interp1d(freq_oe_gain, oe_gain_actual, kind='cubic', fill_value="extrapolate")
oe_gain = interp_oe_gain(freq)

interp_horn_gain = interp1d(freq_horn_gain, horn_gain_actual, kind='cubic', fill_value="extrapolate")
horn_gain = interp_horn_gain(freq)

interp_atten10 = interp1d(freq_atten10, atten10, kind='cubic', fill_value="extrapolate")
interp_atten12 = interp1d(freq_atten12, atten12, kind='cubic', fill_value="extrapolate")
interp_atten14 = interp1d(freq_atten14, atten14, kind='cubic', fill_value="extrapolate")
atten10 = interp_atten10(freq)
atten12 = interp_atten12(freq)
atten14 = interp_atten14(freq)

eirp10 = ref_power + horn_gain + fspl + atten10
eirp12 = ref_power + horn_gain + fspl + atten12
eirp14 = ref_power + horn_gain + fspl + atten14
print(ref_power, horn_gain, fspl, atten14)

# Load received power data
my_subdir = "0724"  # attn10
# my_subdir = ""

csv_files = glob.glob(os.path.join(my_dir, my_subdir, 'RX_RF_2024*.csv'))

# Plotting
# plt.figure()
plt.style.use(['science','ieee','no-latex'])
fig, ax1 = plt.subplots()

# Print the file names
curr_max = -100
curr_argmax = 0
for i,file in enumerate(list(csv_files)):
    print(os.path.basename(file))

    file_name_parse = os.path.basename(file)
    file_name_parse = file_name_parse.split('_')
    file_attn = 10 if file_name_parse[-1] == '10.csv' else 12 if file_name_parse[-1] == '12.csv' else 14

    # file = f'{my_dir}{my_subdir}RX_RF_20240724_1739.csv'
    tmp = pd.read_csv(file).values
    print(tmp.shape)
    if tmp.shape[0] > tmp.shape[1]:
        tmp = tmp.transpose()
    freq_rec_rx = tmp[0, :]
    rec_rx = tmp[1, :]
    # print(freq_rec_rx, rec_rx)
    # Calculate gain and convert to numpy array
    if file_attn == 10:
        interp_eirp = interp1d(freq, eirp10, kind='cubic', fill_value="extrapolate")
    elif file_attn == 12:
        interp_eirp = interp1d(freq, eirp12, kind='cubic', fill_value="extrapolate")
    elif file_attn == 14:
        interp_eirp = interp1d(freq, eirp14, kind='cubic', fill_value="extrapolate")
    gain = rec_rx - interp_eirp(freq_rec_rx) + 3 # 3 dB due to the output balun
    gain = np.array(gain)

    # Calculate smoothed gain with moving average
    window_size = 4
    smoothed_gain = np.convolve(gain, np.ones(window_size)/window_size, mode='same')

    print(file_name_parse)
    os.makedirs(f'{my_dir}{my_subdir}/gain/', exist_ok=True)
    csv_name = f'RX_RFGain_{file_name_parse[-3]}_attn_{file_name_parse[-1]}'
    with open(f'{my_dir}{my_subdir}/gain/{csv_name}', 'w', newline='') as csvfile:
    # print(smoothed_gain, smoothed_gain.max())
        print(csv_name)
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['freq']+ freq_rec_rx[1:len(freq_rec_rx)].tolist())
        csv_writer.writerow(['gain']+ smoothed_gain[1:len(freq_rec_rx)].tolist())

    line_max = smoothed_gain[window_size:len(freq_rec_rx)-window_size].max()
    if line_max > curr_max:
        curr_max = line_max
        curr_argmax = np.argmax(smoothed_gain[window_size:len(freq_rec_rx)-window_size])+window_size
    ax1.plot(freq_rec_rx, gain, label=f'{file_name_parse[-3]}', alpha=0.7)
    ax1.plot(freq_rec_rx[0:len(freq_rec_rx)-window_size], smoothed_gain[0:len(freq_rec_rx)-window_size], label=f'Smoothed {file_name_parse[-3]} attn {file_attn}')

ax=plt.gca()
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=40")
kw = dict(xycoords='data',textcoords="axes fraction",
          arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=6) # 6 for IEEE, 12 for normal
ax.annotate(f'Max gain = {curr_max:.2f} dB', xy=(freq_rec_rx[curr_argmax], curr_max), xytext=(0.94,0.96), **kw)


# ax1.axhline(y=curr_max, color='r', linestyle='--')
# ax1.tick_params(labelsize = 28)
# ax1.set_xlabel('Freq [GHz]',fontsize=30)
# ax1.set_ylabel('Receiver OTA Gain [dB]',fontsize=30)
# ax1.grid(True,linestyle='--', dashes=(5, 10))
# ax1.legend(loc='lower center', fontsize=14)
ax1.axhline(y=curr_max, linestyle='--')
ax1.set_xlabel('Freq [GHz]')
ax1.set_ylabel('Receiver OTA Gain [dB]')
ax1.grid(True,linestyle='--',alpha=0.5)
ax1.legend(loc='lower center',fontsize=7)

xaxis_range = [int(freq_rec_rx[1]), int(freq_rec_rx[-1])]
xticks = np.arange(xaxis_range[0], xaxis_range[1]-0, 5)  # Ticks with a step of 20
ax1.set_xticks(xticks)
yaxis_range = [-70, curr_max+20]

yticks = np.arange(yaxis_range[0]+10, yaxis_range[1]-10, 20)  # Ticks with a step of 20
ax1.set_yticks(yticks)
ax1.set_yticklabels([str(tick) for tick in yticks])

ax1.axis([freq_rec_rx[1],freq_rec_rx[-1],yaxis_range[0],yaxis_range[1]])

ax2 = ax1.twiny()

scale_factor = 18
new_x = freq_rec_rx / scale_factor

# Set the limits and ticks of the new x-axis
ax2.set_xlim(ax1.get_xlim()[0] * scale_factor, ax1.get_xlim()[1] * scale_factor)
ax2.set_xticks(ax1.get_xticks() * scale_factor)
ax2.set_xticklabels([f'{tick/scale_factor:.2f}' for tick in ax1.get_xticks()])
ax2.set_xlabel('LO subharmonic frequency at input [GHz]')

plt.show()
