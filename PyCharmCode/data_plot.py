import numpy as np
import scienceplots
from pylab import *
import matplotlib.pyplot as plt
import skrf as rf
import csv

# LNA
freq = np.linspace(135, 147, 13)
A=[5.12,5.32,5.5,5.72,5.8,6.10,6.20,6.5,6.75,6.8,7.15,7.01,7.24]
B=[6.49,6.76,6.9,7.11,7.23,7.58,7.70,8.08,8.26,8.45,8.76,8.60,8.79]

# plt.style.use(['science','no-latex','ieee'])
plt.style.use(['science','no-latex'])
# plt.figure()
# plt.plot(freq, 20*np.log10(A), label='Rx pad to mixer gate')
# plt.plot(freq, 20*np.log10(B), label='IQ-mixer output to mixer gate')
# plt.title("Voltage Gain to mixer gate")
# plt.legend(loc='lower center')
# plt.xlabel('Frequency(GHz)')
# plt.ylabel('Voltage Gain (dB)')
# plt.axis([134,148,0 ,20])
# plt.show(block=False)
#
# # PA
# freq = np.linspace(130,146,17)
# A = [16.27,16.5,16.51,16.53,16.20,16.24,16.21,16.28,16.18,16.31,16.25,16.71,17.3,17.53,17.50,17.48,17.42]
#
# plt.figure()
# plt.plot(freq,np.subtract(A,5.8),label='PA output power')
# plt.title("$P_{SAT}$")
# # plt.legend(loc='upper left')
# plt.legend(loc='lower center')
# plt.xlabel('frequency(GHz)')
# plt.ylabel('Power (dBm)')
# plt.axis([129,148,5,15])
# plt.show(block=False)
#
# # LO
# f1=[54.00,56.25,58.50,60.75,63.00,65.25,67.50,69.75,72.00,74.25,76.50,78.75,81.00,83.25,85.50,87.75,90.00]
# B=[-36.21,-38.24,-40.27,-29.41,-18.54,-12.71,-6.867,-5.330,-3.792,-4.400,-5.009,-7.213,-9.418,-10.44,-11.46,-11.53,-11.61]
#
# f2=[108,112.5,117,121.5,126,130.5,135,139.5,144,148.5,153,157.5,162,166.5,171,175.5,180,]
# A=[-88.98,-73.12,-57.83,-46.3,-32.83,-6.4,-1.809,-1.89,-1.985,-4.75,-10.59,-20.35,-30.07,-38.92,-47.76,-54.32,-60.88]
#
# plt.figure()
# plt.plot(f2,A,label='18th order harmonic at 140 GHz Stage')
# plt.plot(f1,B,label='9th order harmonic at 70 GHz Stage')
# plt.legend(loc='lower center')
# plt.title("Voltage Gain for LO Multiply Chain")
# plt.axis([50,200,-120,0])
# plt.xlabel('Frequency(GHz)')
# plt.ylabel('Voltage Gain (dB)')
# plt.show(block=False)
#
# #,LNA
# f = np.linspace(135,147,13);
# A = [11.2,10.8,10.5,10.4,10.2,10.25,10.19,10.17,10.09,10.05,10.22,10.2,10.44]
# plt.figure()
# plt.plot(f,A,label='Noise Figure')
# plt.legend(loc='lower center')
# plt.axis([134,148,0,18])
# plt.title("Noise Figure")
# plt.xlabel('Frequency(GHz)')
# plt.ylabel('NF(dB)')
# plt.show()


# Antenna S11
# antenna = rf.Network('test.s34p', f_unit='GHz')
# antenna.plot_s_db(m=31,n=31,label='Full transition structure ')
# antenna.plot_s_db(m=32,n=32,label='Antenna matching only')
# plt.ylabel('S-parameters')
# plt.title('RF transition and antenna matching simulation')
# plt.show()

# Antenna Gain
# csv_name = 'Sim_results/peakgain.csv'
# peakgain = open(csv_name)
# obj_peakgain = csv.reader(peakgain)
# freq1 = []
# peakgain_list = []
# for i,row in enumerate(list(obj_peakgain)):
#     if i == 0:
#         continue
#     # print(row)
#     freq1.append(float(row[0]))
#     peakgain_list.append(float(row[1]))
#
# csv_name = 'Sim_results/peakrealizedgain.csv'
# peakrealizedgain = open(csv_name)
# obj_peakrealizedgain = csv.reader(peakrealizedgain)
# freq2 = []
# peakrealizedgain_list = []
# for i,row in enumerate(list(obj_peakrealizedgain)):
#     if i == 0:
#         continue
#     # print(row)
#     freq2.append(float(row[0]))
#     peakrealizedgain_list.append(float(row[1]))
#
# plt.figure()
# plt.plot(freq1, peakgain_list, label='Peak Gain')
# plt.plot(freq2, peakrealizedgain_list, label='Peak Realized Gain')
# plt.title("Antenna Gain")
# plt.legend(loc='lower center')
# plt.xlabel('Frequency(GHz)')
# plt.ylabel('Voltage Gain (dB)')
# # plt.axis([134,148,0 ,20])
# plt.show()

# Antenna Gain deg
# csv_name = 'Sim_results/antennagaindeg.csv'
# peakgain = open(csv_name)
# obj_peakgain = csv.reader(peakgain)
# deg1 = []
# deg2 = []
# gain_0 = []
# gain_90 = []
# for i,row in enumerate(list(obj_peakgain)):
#     if i == 0:
#         continue
#     # print(row)
#     if float(row[1]) == 0:
#         deg1.append(float(row[2]))
#         gain_0.append(float(row[3]))
#     else:
#         deg2.append(float(row[2]))
#         gain_90.append(float(row[3]))
#
# plt.figure()
# plt.plot(deg1, gain_0, label='Gain at $\phi$=0 deg')
# plt.plot(deg2, gain_90, label='Gain at $\phi$=90 deg')
# plt.title("Antenna Gain vs $\\theta$")
# plt.legend(loc='lower center')
# plt.xlabel('$\\theta(deg)$')
# plt.ylabel('Gain (dBi)')
# plt.axis([134,148,0 ,20])
# plt.show()

# Leakage cancellation
# csv_name = 'Sim_results/leakage_cancel_20cm.csv'
# signal = open(csv_name)
# obj_signal = csv.reader(signal)
# dist = []
# raw = []
# cancelled = []
# leakage_only = []
# target_only = []
# for i,row in enumerate(list(obj_signal)):
#     # print(row)
#     dist.append(float(row[0]))
#     raw.append(float(row[1]))
#     cancelled.append(float(row[2]))
#     leakage_only.append(float(row[3]))
#     target_only.append(float(row[4]))
#
# correction_dist = 14.229
# plt.figure()
# plt.plot(dist, raw, label='before cancellation',linestyle='-.')
# plt.plot(np.subtract(dist, correction_dist), cancelled,marker='.', label='after cancellation')
# plt.plot(dist, leakage_only, label='leakage-only',linestyle='dashed')
# plt.plot(dist, target_only, label='target-only',linestyle='dashed')
#
# plt.title("Range FFT before and after leakage cancellation")
# plt.legend(loc='upper right')
# plt.xlabel('Distance (mm)')
# plt.ylabel('Power (dB)')
# plt.axis([0,1000,-140 ,0])
# plt.show()


# LO chain
# csv_name = 'Sim_results/gain_vs_flo.csv'
# powerout = open(csv_name)
# obj_powerout = csv.reader(powerout)
# flo = []
# gain = []
# for i,row in enumerate(list(obj_powerout)):
#     if i == 0:
#         continue
#     flo.append(float(row[0]))
#     gain.append(float(row[1]))
# plt.rcParams['axes.unicode_minus'] = False
# plt.figure()
# plt.plot(flo, gain, label='Rx output power')
# plt.title("Fundamental tone power vs LO frequency")
# plt.legend(loc='lower center')
# plt.xlabel('Frequency (GHz)')
# plt.ylabel('Gain (dB)')
# plt.axis([7,8,-40 ,-20])
# plt.show()

Tchirp = 100E-6
fsample = 100E6
fbeat = 10000
tstep = 1/fsample
t = np.linspace(0, Tchirp*5, int(Tchirp*5/tstep))
s = np.cos(fbeat*(t % Tchirp))
sf = 10*np.log10(np.fft.fft(s))
freq = np.linspace(0,len(t),len(t))
# fig = plt.subplots(1,2)
plt.figure()
plt.subplot(2,1,1)
plt.plot(t, s, label='beat tone')
plt.xlabel('Time (s)')
plt.title("Non-integer period signal")

plt.subplot(2,1,2)
plt.plot(freq[0:20], sf[0:20], label='spectrum')
plt.xlabel('Frequency Index')

plt.title("FFT for non-integer period signal")
plt.rcParams['axes.unicode_minus'] = False
plt.tight_layout()
plt.show()