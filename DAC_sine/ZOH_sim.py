import numpy as np
import matplotlib.pyplot as plt

N_harm = 3
f_sampling = 10_000_000
f_signal = np.linspace(1, 20, 4) * 10_000
f = np.linspace(1, f_sampling * N_harm, 100* N_harm)
stem_bottom = -80  # dB

sci = np.printoptions(precision=3, suppress = True)


def scale_MHz(x):
    return x/1e6


def zoh(f, f_sampling):
    T = 1 / f_sampling
    return np.exp(-1j * np.pi * f * T) * np.sinc(f * T)


def mag_rsp(H):
    return np.abs(H)


def dB(H):
    return 20*np.log10(H)


def zoh_conv(f, f_sampling):
    f_out = f
    for i in range(1,5+1):
        f_out = np.concatenate((f_out, i*f_sampling-f[::-1], i*f_sampling+f))
    S_out = zoh(f_out, f_sampling)
    return f_out, S_out


H_f = zoh(f, f_sampling)
S_f = zoh(f_signal, f_sampling)
f_out, S_out = zoh_conv(f_signal, f_sampling)


print(f'Sampling Frequency = {scale_MHz(f_sampling)} MHz')
with sci:
    print(f'f_out = {f_out}')
    print(f'S_out_dB = {dB(mag_rsp(S_out))}')
fig, ax = plt.subplots(nrows=2, ncols=1)
ax[0].clear()
ax[0].plot(scale_MHz(f), mag_rsp(H_f))
ax[0].stem(scale_MHz(f_out), mag_rsp(S_out), bottom=0)
ax[0].set_xlabel('MHz')
ax[0].set_title('Mag')
ax[0].set_xlim(0, N_harm * scale_MHz(f_sampling))

ax[1].clear()
ax[1].plot(scale_MHz(f), dB(mag_rsp(H_f)))
ax[1].stem(scale_MHz(f_out), dB(mag_rsp(S_out)), bottom=stem_bottom)
ax[1].set_xlabel('MHz')
ax[1].set_title('dB scale')
ax[1].set_ylim(stem_bottom,3)
ax[1].set_xlim(0, N_harm * scale_MHz(f_sampling))

plt.suptitle('Zero-order-hold DAC Frequency Response')
fig.tight_layout()
plt.show()