import numpy as np
import matplotlib.pyplot as plt

alpha = 1
beta = 0.25

mags = []
est_mags = []
error_mags = []
for i in range(100):
    num_i = np.random.rand()
    num_q = np.random.rand()
    # print(num_i, num_q)

    mag = np.sqrt(num_i**2+num_q**2)
    mags.append(mag)
    est_mag = alpha * max(abs(num_i), abs(num_q)) + beta * min(abs(num_i), abs(num_q))
    est_mags.append(est_mag)

    error_mags.append(np.subtract(mag, est_mag))

relative_errs = np.divide(error_mags, mags)
rms_err = np.sqrt(np.mean(np.square(relative_errs)))
rms_err_dB = 20*np.log10(np.sqrt(np.mean(np.square(relative_errs))))

fig, axes = plt.subplots(nrows=4, ncols=1)
axes[0].plot(mags,label='actual mag', marker='x', color='b')
axes[0].plot(est_mags, label='estimated mag', marker='s', color='r')
axes[0].set_title('Magnitude vs Estimation')
axes[0].legend()

axes[1].plot(error_mags, label='error', marker='x', color='b')
axes[1].set_title('Absolute Error (linear)')

axes[2].plot(relative_errs, label='error', marker='x', color='b')
axes[2].set_title('Relative Error (linear), rms error (relative) ='+str(rms_err))

axes[3].plot(20*np.log10(abs(relative_errs)), label='error', marker='x', color='r')
axes[3].set_ylabel('dB')
axes[3].set_title('Error (dB), rms error (relative) in dB ='+str(rms_err_dB))
fig.tight_layout()
plt.show()