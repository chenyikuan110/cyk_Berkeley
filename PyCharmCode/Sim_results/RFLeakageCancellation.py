import numpy as np
import scienceplots
import matplotlib.pyplot as plt
# import skrf as rf
# from scipy.signal import hanning, boxcar, windows
from scipy.constants import c
from pylab import *

rcParams["axes.unicode_minus"] = False
plt.style.use(['science','no-latex'])
# plt.style.use(['science','no-latex','ieee'])

# multi-path on/off
multipath = False

# plot options
plot_steps = False
window_type = hamming

IQ_mismatch_on = 0  # set to 0 to turn off IQ amplitude mismatch
noise_on = 1  # set to 0 to turn off thermal noise
averaging = 1  # if average is turned on, the frequency detection will be smoothed

num_averaging = 3  # using neighboring plus_minus num_average indexes

def triang(M):
    if M <= 0:
        return np.array([])
    if M == 1:
        return np.ones(1)
    n = np.arange(0, M)
    return 1 - np.abs((n - (M - 1) / 2) / (M / 2))

def hamming(M):
    if M < 1:
        return np.array([])
    if M == 1:
        return np.ones(1)
    n = np.arange(0, M)
    return 0.54 - 0.46 * np.cos(2.0 * np.pi * n / (M - 1))

'''
    Parameter initialization
'''
avg_window = triang(2 * num_averaging + 1)
avg_window = avg_window / np.sum(avg_window)

fRF = 135e9
fBW = 10e9
Tchirp = 100e-6
K = fBW / Tchirp

fRBW = 1 / Tchirp
dRBW = fRBW / fBW * c * Tchirp
fsampling = fRBW * 1000
N = int(np.floor(fsampling / fRBW))

PTX_dBm = 10
# gain_rx = 40
Isolation = 30  # dB
Isolation_1 = 45  # dB

t = np.linspace(0, Tchirp * (1 - 1 / N), N)  # simulate one chirp
window = window_type(len(t))
# print(window)
window = window * len(window) / np.sum(window)

fig_count = 0

f_range = 1 / 2 * 10e3
# num_points = 3
num_bin_2nd_leakage = 6
leak_dist = 1.7e-3 + np.random.rand() * 0.6e-3
leak_dist_1 = dRBW*num_bin_2nd_leakage + np.random.rand() * 0.1e-3  # second jammer

tau_leak = leak_dist / c
tau_leak_1 = leak_dist_1 / c

tau_LORX = (500e-6 * np.random.rand()) / c  # relative delay from LO splitter to RX mixer-input, make it a bit random

delay_step = 1.53e-12
tau_tunable_array = np.arange(0, 120e-12, delay_step)
del_0 = np.zeros(len(tau_tunable_array))
del_2 = del_0.copy()
yfft_1 = del_2.copy()  # bin[1] bookkeeping

curr_max_del_0 = 0
curr_max_del_2 = 0
curr_max_tau = 0
curr_tau = tau_tunable_array[0]

DC_offset = np.random.randn() * 0.001

Phi_0 =  2 * np.pi * np.random.rand()  # LO start at a random phase at t=0
Phi_1 = 0 * 2 * np.pi * np.random.rand() / 360 / 2  # keep the phase mismatch in the LO splitter less than 0.5 deg

sharpness_change = 0


# helper
def db2mag(db):
    return 10 ** (db / 20)


def mag2db(mag):
    return 20 * np.log10(mag)


A0 = db2mag(PTX_dBm - Isolation) * np.sqrt(2)  # sqrt(2) as the crest factor of sine
A1 = db2mag(PTX_dBm - Isolation_1) * np.sqrt(2)

IQ_mismatch = 1 * db2mag(-0.5 * IQ_mismatch_on)
IQ_phase_err = 1 * np.pi / 180  # phase error in IQ hybrid

SNRdB = 114  # relative to 0dBm full-scale; for 1000pts
sigma = noise_on * 10 ** (SNRdB / 10)  # SNR to linear scale
N0 = 1 / sigma
Noise_i = np.sqrt(N0 / 2) * np.random.randn(len(t))  # computed noise
Noise_q = np.sqrt(N0 / 2) * np.random.randn(len(t))  # computed noise

LO = np.cos((2 * np.pi * (fRF + K / 2 * (t - tau_LORX)) * (t - tau_LORX) + Phi_0 + Phi_1)) \
     + 1j * np.sin((2 * np.pi * (fRF + K / 2 * (t - tau_LORX)) * (t - tau_LORX) + Phi_0 + Phi_1 + IQ_phase_err))

'''
    Now start the loop to find the correct delay to achieve leakage beat frequency alignment with FFT bin
'''

for tau in tau_tunable_array:
    f_beat = K * (tau_leak + tau)
    # RF down-conversion
    leakage_controlled_i = 1 * A0 * np.cos(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak + tau))) * (t - (tau_leak + tau)) + Phi_0) + Noise_i
    leakage_controlled_q = 1 * A0 * (IQ_mismatch) * np.sin(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak + tau))) * (t - (tau_leak + tau)) + Phi_0) + Noise_q

    if multipath == True:
        f_beat_1 = K * (tau_leak_1 + tau)
        leakage_controlled_i += A1 * np.cos(
            2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + tau))) * (t - (tau_leak_1 + tau)) + Phi_0)
        leakage_controlled_q += A1 * np.sin(
            2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + tau))) * (t - (tau_leak_1 + tau)) + Phi_0)

    y = leakage_controlled_i * np.real(LO) + leakage_controlled_q * np.imag(LO) + DC_offset

    # windowing
    # y = y * window  # cannot window it, weird

    yfft = np.fft.fft(y) / len(y)
    yfft_db = 20 * np.log10(np.abs(yfft))

    yfft_1[fig_count] = yfft_db[1]
    del_0[fig_count] = yfft_db[1] - yfft_db[0]
    del_2[fig_count] = yfft_db[1] - yfft_db[2]

    if averaging == 0:
        if del_0[fig_count] > curr_max_del_0:
            curr_max_del_0 = del_0[fig_count]

        if del_2[fig_count] > curr_max_del_2:
            curr_max_del_2 = del_2[fig_count]
            curr_max_tau = tau

        if del_0[fig_count] < curr_max_del_0 or del_2[fig_count] < curr_max_del_2:
            # fig_count
            # calculate the change of sharpness
            sharpness_change = curr_max_del_0 - del_0[fig_count] + curr_max_del_2 - del_2[fig_count]
            if sharpness_change > 300:
                # curr_tau
                break

    curr_tau = tau

    fig_count += 1

if averaging == 1:
    curr_max_del_0 = 0
    curr_max_del_2 = 0
    del_0_avg = del_0.copy()
    del_2_avg = del_2.copy()

    for fig_count in range(1 + num_averaging, len(tau_tunable_array) - num_averaging):
        del_0_avg[fig_count] = np.dot(del_0[fig_count - num_averaging:fig_count + num_averaging + 1], avg_window)
        del_2_avg[fig_count] = np.dot(del_2[fig_count - num_averaging:fig_count + num_averaging + 1], avg_window)

        if del_0_avg[fig_count] > curr_max_del_0:
            curr_max_del_0 = del_0_avg[fig_count]
            # curr_max_tau = tau_tunable_array[fig_count]

        if del_2_avg[fig_count] > curr_max_del_2:
            curr_max_del_2 = del_2_avg[fig_count]
            curr_max_tau = tau_tunable_array[fig_count]

        if del_0_avg[fig_count] < curr_max_del_0 or del_2_avg[fig_count] < curr_max_del_2:
            # fig_count
            # calculate the change of sharpness
            sharpness_change = curr_max_del_0 - del_0_avg[fig_count] + curr_max_del_2 - del_2_avg[fig_count]
            if sharpness_change > 300:
                # curr_tau
                break

    del_0 = del_0_avg
    del_2 = del_2_avg  # replace

# actual phase of the leakage at RX mixer RF port - this is black-boxed to
# the system, the minus sign is because Rx lags behind LO by the tau
# leak_phase = rem(2*pi*(fRF+K/2*(-tau_leak-curr_max_tau))*(-tau_leak-curr_max_tau), 2*pi);
leak_phase = np.remainder(
    2 * np.pi * (tau_leak + curr_max_tau - tau_LORX) * (fRF - K / 2 * (tau_leak + curr_max_tau - tau_LORX)), 2 * np.pi)
if leak_phase < 0:
    leak_phase += 2 * np.pi

fig_count += 1
plt.figure(fig_count)

leak_dist_det = (fRBW / K - curr_max_tau) * 3e8

plt.plot(tau_tunable_array, del_0, label='P(1)-P(0)')
plt.plot(tau_tunable_array, del_2, label='P(1)-P(2)')
plt.axis([tau_tunable_array[0], tau_tunable_array[-1], -5, 50])
plt.legend()
plt.ylabel('dB')
plt.xlabel('${\\tau}_{tunable}$')
plt.title(r'Sharpness of the peak with ${\tau}$ sweep '
          f'leakage path set to {leak_dist * 1000:.3f} mm, \n'
          f'leakage path detected is {leak_dist_det * 1000:.3f} mm.,\n'
          f'number of iterations {fig_count - 1}')
plt.tight_layout()
plt.show(block=False)

plt.figure(fig_count + 1)
plt.plot(tau_tunable_array, yfft_1)
plt.ylabel('dB')
plt.xlabel('${\\tau}_{tunable}$')
plt.title('bin[1] power')
plt.tight_layout()
plt.show(block=False)

# now calculate the amplitude and phase of the controlled leakage
leakage_controlled_i = 1 * A0 * np.cos(
    2 * np.pi * (fRF + K / 2 * (t - (tau_leak + curr_max_tau))) * (t - (tau_leak + curr_max_tau)) + Phi_0) + Noise_i
leakage_controlled_q = 1 * A0 * (IQ_mismatch) * np.sin(
    2 * np.pi * (fRF + K / 2 * (t - (tau_leak + curr_max_tau))) * (t - (tau_leak + curr_max_tau)) + Phi_0) + Noise_q

if multipath == True:
    leakage_controlled_i += A1 * np.cos(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau))) * (t - (tau_leak_1 + curr_max_tau)) + Phi_0)
    leakage_controlled_q += A1 * np.sin(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau))) * (t - (tau_leak_1 + curr_max_tau)) + Phi_0)

# y = leakage_controlled_i * np.real(LO) + leakage_controlled_q * np.imag(LO) + DC_offset
y = leakage_controlled_i * np.real(LO) + leakage_controlled_q * np.imag(LO) + DC_offset

# windowing
y = y * window
yfft = np.fft.fft(y) / len(y)

# parameter estimation
A0_hat = np.abs(yfft[1]) * 2  # first bin
Phi_hat_0 = np.angle(yfft[1])

# Phi_hat_0 = 2*pi*fRF/K*fRBW

# generate a signal with leakage plus target
dist_tar = 0.24  # meter, hand is this far away
tau_tar = dist_tar * 2 / 3e8

# Ptx = 17  # transmitted power in dBm
Ap = 7.3e-7  # Rx antenna aperture, assuming 3dBi gain
RCS_dB = -40  # dBsm
RCS = 10 ** (RCS_dB / 10)

# amp of received signal
Atar_dB = PTX_dBm + 10 * np.log10(2 * Ap * RCS / (4 * np.pi) ** 2 / dist_tar ** 4)
Atar = db2mag(Atar_dB) * np.sqrt(2)

# book keeping
# the pure/untuned leakage has an un-controlled delay
leakage_uncontrolled_i = 1 * A0 * np.cos(2 * np.pi * (fRF + K / 2 * (t - tau_leak)) * (t - tau_leak) + Phi_0) + Noise_i
leakage_uncontrolled_q = 1 * A0 * (IQ_mismatch) * np.sin(
    2 * np.pi * (fRF + K / 2 * (t - tau_leak)) * (t - tau_leak) + Phi_0) + Noise_q

if multipath == True:
    leakage_uncontrolled_i += A1 * np.cos(2 * np.pi * (fRF + K / 2 * (t - tau_leak_1)) * (t - tau_leak_1) + Phi_0)
    leakage_uncontrolled_q += A1 * np.sin(2 * np.pi * (fRF + K / 2 * (t - tau_leak_1)) * (t - tau_leak_1) + Phi_0)

# purely target
tar_only_uncontrolled_i = 1 * Atar * np.cos(2 * np.pi * (fRF + K / 2 * (t - tau_tar)) * (t - tau_tar) + Phi_0)
tar_only_uncontrolled_q = 1 * Atar * (IQ_mismatch) * np.sin(
    2 * np.pi * (fRF + K / 2 * (t - tau_tar)) * (t - tau_tar) + Phi_0)

tar_only_controlled_i = 1 * Atar * np.cos(
    2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau)) * (t - tau_tar - curr_max_tau) + Phi_0)
tar_only_controlled_q = 1 * Atar * (IQ_mismatch) * np.sin(
    2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau)) * (t - tau_tar - curr_max_tau) + Phi_0)

# received signal if leakage is not tuned
Rx_i_uncontrolled = leakage_uncontrolled_i + tar_only_uncontrolled_i + Noise_i
Rx_q_uncontrolled = leakage_uncontrolled_q + tar_only_uncontrolled_q + Noise_q

# received signal if leakage is tuned
Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i
Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q

# Phase tuning array
Phi_tunable_array = np.arange(Phi_hat_0 - np.pi, Phi_hat_0 + np.pi, 0.01)
BB_del_0 = np.zeros(len(Phi_tunable_array))
BB_del_2 = np.zeros(len(Phi_tunable_array))
BB_fft_1 = np.zeros(len(Phi_tunable_array))  # bin[1] bookkeeping

curr_min_BB_del_0 = 0
curr_min_BB_del_2 = 0
curr_min_BB_Phi = 0
curr_BB_Phi = Phi_tunable_array[0]

'''
    Find the correct phase for DAC to cancel the leakage
'''

plot_count = 0

# Sweep to find the best initial phase for the cancellation signal
for Phi_hat in Phi_tunable_array:
    DAC_IF = 1 * A0_hat * np.exp(1j * (2 * np.pi * fRBW * t + Phi_hat))
    y_cancel = DAC_IF * LO

    out_i = Rx_i_controlled - np.real(y_cancel)
    out_q = Rx_q_controlled - np.imag(y_cancel)

    # Dechirp
    BB_out = out_i * np.real(LO) + out_q * np.imag(LO) + DC_offset

    # Windowing
    BB_out = BB_out * window

    BB_fft = np.fft.fft(BB_out) / len(BB_out)
    BB_fft_db = mag2db(np.abs(BB_fft))

    BB_del_0[plot_count - 1] = BB_fft_db[1]
    BB_del_2[plot_count - 1] = BB_fft_db[1]
    BB_fft_1[plot_count - 1] = BB_fft_db[1]

    string_phi = f"Phi: {Phi_hat}, BB_del_0: {BB_del_0[plot_count - 1]}"
    print(string_phi)

    if BB_del_0[plot_count - 1] < curr_min_BB_del_0:
        curr_min_BB_del_0 = BB_del_0[plot_count - 1]
        curr_min_BB_Phi = Phi_hat

    if BB_del_0[plot_count - 1] > curr_min_BB_del_0 or BB_del_2[plot_count - 1] > curr_min_BB_del_2:
        sharpness_change = curr_min_BB_del_0 - BB_del_0[plot_count - 1] + curr_min_BB_del_2 - BB_del_2[plot_count - 1]
        if sharpness_change < -300:
            break

    curr_BB_Phi = Phi_hat
    plot_count += 1

leak_phase_det = np.remainder(curr_min_BB_Phi, 2 * np.pi)
if leak_phase_det < 0:
    leak_phase_det += 2 * np.pi

plt.figure(plot_count)
plt.plot(Phi_tunable_array, BB_del_0, label='P(1)-P(0)')
plt.plot(Phi_tunable_array, BB_del_2, label='P(1)-P(2)')
plt.axis([Phi_tunable_array[0], Phi_tunable_array[-1], -50, 50])
plt.legend()
plt.ylabel('dB')
plt.xlabel('${\\Phi}_{tunable} rad$')
plt.title(f'Sharpness of the peak with phase sweep \n'
          f'leakage phase offset actually set to {leak_phase:.3f} rad \n'
          f'leakage phase offset detected is {leak_phase_det:.3f} rad. \n'
          f'number of iterations {plot_count - 1}')

plt.figure(plot_count + 1)
plt.plot(Phi_tunable_array, BB_fft_1)
plt.ylabel('dB')
plt.xlabel('${\\Phi}_{tunable} rad$')
plt.title('bin[1] power')

plt.show(block=False)

# Kill the dominant one and keep working on the second one
if multipath == True:
    curr_max_tau_0 = 0
    curr_max_del_0 = 0
    curr_max_del_2 = 0
    fig_count = 1

    for tau in tau_tunable_array:
        # A_i*cos⁡( 2π(f_RF+K/2 t-Kτ_i)t-2π (f_RF-K/2 τ_i)τ_i+φ(t-τ_i ))
        f_DAC = fRBW + K * tau  # derivation in word
        Phi_DAC = Phi_hat_0 + 2 * np.pi * (fRF - K / 2 * tau) * tau  # derivation in word
        DAC_IF = 1 * A0_hat * np.exp(1j * (2 * np.pi * f_DAC * t + Phi_DAC))

        y_cancel = DAC_IF * LO
        leakage_controlled_i += A1 * np.cos(
            2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau + tau))) * (
                        t - (tau_leak_1 + curr_max_tau + tau)) + Phi_0
        )
        leakage_controlled_q += A1 * np.sin(
            2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau + tau))) * (
                        t - (tau_leak_1 + curr_max_tau + tau)) + Phi_0
        )

        tar_only_controlled_i = 1 * Atar * np.cos(
            2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau - tau)) * (t - tau_tar - curr_max_tau - tau) + Phi_0
        )
        tar_only_controlled_q = 1 * Atar * IQ_mismatch * np.sin(
            2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau - tau)) * (t - tau_tar - curr_max_tau - tau) + Phi_0
        )
        Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i
        Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q

        out_i = Rx_i_controlled - np.real(y_cancel)
        out_q = Rx_q_controlled - np.imag(y_cancel)

        # Dechirp
        BB_out = out_i * np.real(LO) + out_q * np.imag(LO) + DC_offset

        # Windowing
        yfft = np.fft.fft(BB_out) / len(BB_out)
        yfft_db = mag2db(np.abs(yfft))

        yfft_1[fig_count - 1] = yfft_db[num_bin_2nd_leakage]
        del_0[fig_count - 1] = yfft_db[num_bin_2nd_leakage] - yfft_db[num_bin_2nd_leakage-1]
        del_2[fig_count - 1] = yfft_db[num_bin_2nd_leakage] - yfft_db[num_bin_2nd_leakage+1]

        if del_0[fig_count - 1] > curr_max_del_0:
            curr_max_del_0 = del_0[fig_count - 1]

        if del_2[fig_count - 1] > curr_max_del_2:
            curr_max_del_2 = del_2[fig_count - 1]
            curr_max_tau_0 = tau

        if del_0[fig_count - 1] < curr_max_del_0 or del_2[fig_count - 1] < curr_max_del_2:
            sharpness_change = curr_max_del_0 - del_0[fig_count - 1] + curr_max_del_2 - del_2[fig_count - 1]
            if sharpness_change > 300:
                break

        fig_count += 1

    plt.figure()

    leak_dist_det = (fRBW / K - curr_max_tau_0) * 3e8

    plt.plot(tau_tunable_array, del_0, label='P(1)-P(0)')
    plt.plot(tau_tunable_array, del_2, label='P(1)-P(2)')
    plt.axis([tau_tunable_array[0], tau_tunable_array[-1], -5, 50])
    plt.legend()
    plt.ylabel('dB')
    plt.xlabel('${\\tau}_{tunable}$')
    plt.title(r'Sharpness of the peak with ${\\tau}_{tunable}$ sweep'
              f'leakage path set to {leak_dist_1 * 1000} mm\n'
              f'leakage path detected is {(dRBW*num_bin_2nd_leakage + leak_dist_det) * 1000} mm.\n'
              f'number of iterations {fig_count - 1}')

    plt.figure(fig_count + 1)
    plt.plot(tau_tunable_array, yfft_1)
    plt.ylabel('dB')
    plt.xlabel('${\\tau}_{tunable}$')
    plt.title(f'bin[{num_bin_2nd_leakage}] power')

    # Now calculate the amplitude and phase of the controlled leakage
    f_DAC = fRBW - K * curr_max_tau_0  # derivation in word
    Phi_DAC = Phi_hat_0 + 2 * np.pi * (fRF - K / 2 * curr_max_tau_0) * curr_max_tau_0  # derivation in word
    DAC_IF = 1 * A0_hat * np.exp(1j * (2 * np.pi * f_DAC * t + Phi_DAC))

    y_cancel = DAC_IF * LO

    leakage_controlled_i += A1 * np.cos(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau + curr_max_tau_0))) * (
                    t - (tau_leak_1 + curr_max_tau + curr_max_tau_0)) + Phi_0
    )
    leakage_controlled_q += A1 * np.sin(
        2 * np.pi * (fRF + K / 2 * (t - (tau_leak_1 + curr_max_tau + curr_max_tau_0))) * (
                    t - (tau_leak_1 + curr_max_tau + curr_max_tau_0)) + Phi_0
    )

    tar_only_controlled_i = 1 * Atar * np.cos(
        2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau - curr_max_tau_0)) * (
                    t - tau_tar - curr_max_tau - curr_max_tau_0) + Phi_0
    )
    tar_only_controlled_q = 1 * Atar * IQ_mismatch * np.sin(
        2 * np.pi * (fRF + K / 2 * (t - tau_tar - curr_max_tau - curr_max_tau_0)) * (
                    t - tau_tar - curr_max_tau - curr_max_tau_0) + Phi_0
    )
    Rx_i_controlled = leakage_controlled_i + tar_only_controlled_i + Noise_i
    Rx_q_controlled = leakage_controlled_q + tar_only_controlled_q + Noise_q

    out_i = Rx_i_controlled - np.real(y_cancel)
    out_q = Rx_q_controlled - np.imag(y_cancel)

    # Dechirp
    BB_out = out_i * np.real(LO) + out_q * np.imag(LO) + DC_offset

    # Windowing
    y = BB_out * window
    yfft = np.fft.fft(y) / len(y)

    # Parameter estimation
    A1_hat = np.abs(yfft[2]) * 2  # second bin
    Phi_hat_1 = np.angle(yfft[2])

'''
    Perform the final cancellation
'''

# Generate cancellation signal
if multipath == 0:
    DAC_IF = 1 * A0_hat * np.exp(1j * (2 * np.pi * fRBW * t + curr_min_BB_Phi))
else:
    # DAC_IF = (1 * A0_hat * np.exp(1j * (2 * np.pi * fRBW * t + curr_min_BB_Phi)) +
    #           1 * A1_hat * np.exp(1j * (2 * np.pi * (fRBW * 2) * t + Phi_hat_1)))
    f_DAC_1 = fRBW + K * curr_max_tau_0  # derivation in word
    f_DAC_2 = fRBW*num_bin_2nd_leakage  # derivation in word
    Phi_DAC_1 = curr_min_BB_Phi + + 2 * np.pi * (fRF - K / 2 * curr_max_tau_0) * curr_max_tau_0
    DAC_IF = (1 * A0_hat * np.exp(1j * (2 * np.pi * f_DAC_1 * t + curr_min_BB_Phi)) +
              1 * A1_hat * np.exp(1j * (2 * np.pi * f_DAC_2 * t + Phi_hat_1)))

y_cancel = DAC_IF * LO

# Cancellation amplitude error
amp_err = db2mag(-1)
out_i = Rx_i_controlled - amp_err * np.real(y_cancel)
out_q = Rx_q_controlled - amp_err * np.imag(y_cancel)

BB_before_controlled = np.real(Rx_i_controlled * np.real(LO) + Rx_q_controlled * np.imag(LO) + DC_offset)
BB_out = np.real(out_i * np.real(LO) + out_q * np.imag(LO) + DC_offset)

# Plot the raw result
BB_raw_out = np.real(Rx_i_uncontrolled * np.real(LO) + Rx_q_uncontrolled * np.imag(LO))

# Plot the leakage only
BB_leakage_out = np.real(leakage_uncontrolled_i * np.real(LO) + leakage_uncontrolled_q * np.imag(LO))

# Plot shifted leakage
BB_leakage_controlled = np.real(leakage_controlled_i * np.real(LO) + leakage_controlled_q * np.imag(LO) + DC_offset)

# Plot the target only
BB_target_out = np.real(tar_only_uncontrolled_i * np.real(LO) + tar_only_uncontrolled_q * np.imag(LO))

# Windowing
BB_out_windowed = BB_out * window
BB_before_controlled_windowed = BB_before_controlled * window
BB_raw_out_windowed = BB_raw_out * window
BB_leakage_out_windowed = BB_leakage_out * window
BB_target_out_windowed = BB_target_out * window

BB_fft = np.fft.fft(BB_out_windowed) / len(BB_out_windowed)
BB_fft_db = mag2db(np.abs(BB_fft)) 


BB_fft_db = BB_fft_db 
BB_before_controlled_fft_db = mag2db(
    np.abs(np.fft.fft(BB_before_controlled_windowed) / len(BB_before_controlled_windowed)))
BB_raw_fft_db = mag2db(np.abs(np.fft.fft(BB_raw_out_windowed) / len(BB_raw_out_windowed)))
BB_leakage_out_db = mag2db(np.abs(np.fft.fft(BB_leakage_out_windowed) / len(BB_leakage_out_windowed)))
BB_target_out_db = mag2db(np.abs(np.fft.fft(BB_target_out_windowed) / len(BB_target_out_windowed)))

gain_rx = -np.max(BB_raw_fft_db)

BB_fft_db = BB_fft_db + gain_rx
BB_before_controlled_fft_db = BB_before_controlled_fft_db+ gain_rx
BB_raw_fft_db = BB_raw_fft_db+ gain_rx
BB_leakage_out_db = BB_leakage_out_db+ gain_rx
BB_target_out_db = BB_target_out_db+ gain_rx
# Plotting the results
plt.figure(plot_count + 2)

# Correct for the additional distance added, unit mm
stem_bottom = -140  # dB
if not multipath:
    correction_dist = curr_max_tau * 3e11 / 2
else:
    correction_dist = (curr_max_tau+curr_max_tau_0) * 3e11 / 2

# markerline1, stemline1, baseline1,  = plt.stem((np.arange(len(BB_raw_fft_db) // 2)) * fRBW * 3e11 / K / 2, BB_raw_fft_db[:len(BB_raw_fft_db) // 2],
#          markerfmt='s', basefmt=' ',   label='before cancellation', linefmt='C0-', 
#          bottom=stem_bottom)

# markerline2, stemline2, baseline2,  = plt.stem((np.arange(len(BB_fft_db) // 2)) * fRBW * 3e11 / K / 2 - correction_dist, BB_fft_db[:len(BB_fft_db) // 2],
#          markerfmt='*', basefmt=' ',   label='after cancellation', linefmt='C1-',
#          bottom=stem_bottom)
plt.plot((np.arange(len(BB_raw_fft_db) // 2)) * fRBW * 3e11 / K / 2, BB_raw_fft_db[:len(BB_raw_fft_db) // 2], 
         label='before cancellation', linewidth = 4,linestyle ='-',color='black', marker='D', markersize=10)

plt.plot((np.arange(len(BB_fft_db) // 2)) * fRBW * 3e11 / K / 2 - correction_dist, BB_fft_db[:len(BB_fft_db) // 2], 
         label='after cancellation' , linewidth = 4,linestyle ='-',color='red', marker='*', markersize=10)

plt.plot((np.arange(len(BB_leakage_out_db) // 2)) * fRBW * 3e11 / K / 2,
         BB_leakage_out_db[:len(BB_leakage_out_db) // 2], linewidth = 4,linestyle ='--',color='blue',
         label='leakage-only')

plt.plot((np.arange(len(BB_target_out_db) // 2)) * fRBW * 3e11 / K / 2, BB_target_out_db[:len(BB_target_out_db) // 2], linewidth = 2, linestyle ='--',
         label='target-only',color='black')

# plt.setp(markerline1, markersize=10, color='gray')
# plt.setp(markerline2, markersize=10, color='red')
# plt.setp(stemline1,  color='black')
# plt.setp(stemline2, color='red')
plt.tick_params(labelsize = 28*2)
plt.axis([0, min((len(BB_fft_db) // 2 - 1) * fRBW * 3e11 / K / 2 - correction_dist, 1000), -125, np.max(BB_raw_fft_db)])
# plt.title(f"Target at {dist_tar * 100} cm, Delay tuning step is {delay_step * 1e12} ps")
# plt.title(f"Simulated 1000-point Range FFT with Target at {dist_tar * 100} cm",fontsize=40)
plt.xlabel('Distance [mm]',fontsize=45)
plt.grid(True,linestyle='--', linewidth=4, alpha=0.5, dashes=(5, 10))
plt.ylabel('Simulated Normalized RX Power [dB]',fontsize=35)
plt.legend(loc='upper right',fontsize=50,bbox_to_anchor=(1, 1))
for i in range(min(100, len(BB_raw_fft_db))):
    print(f"{i * fRBW * 3e11 / K / 2},{BB_raw_fft_db[i]},{BB_fft_db[i]},{BB_leakage_out_db[i]},{BB_target_out_db[i]}")

plt.show()
exit()
# Real Time Plot
# plt.figure(plot_count + 3)
fig, (ax1, ax2) = plt.subplots(2, 1)

# plt.subplot(2, 1, 1)
ax1.plot(t, BB_raw_out, linewidth=2, label='before cancellation')
ax1.plot(t, BB_leakage_out, linewidth=2, label='leakage component')
ax1.legend()
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Magnitude')
ax1.set_title("Signal without frequency offsetting")

# fig, ax1 = plt.subplot(2, 1, 2)
ax2.plot(t, BB_before_controlled, linewidth=2, label='shifted, before cancellation')
ax2.plot(t, BB_leakage_controlled, linewidth=2, label='shifted, leakage component')
ax2.plot(t, np.real(DAC_IF), linewidth=2, label='DAC IF')
ax2.plot(t, BB_out, linewidth=2, label='after cancellation')

ax3 = ax2.twinx()
ax3.plot(t, BB_target_out, linewidth=2, label='target-only')

ax2.legend()
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Magnitude')
ax2.set_title("Signal with frequency offsetting")
plt.tight_layout()
plt.show()
