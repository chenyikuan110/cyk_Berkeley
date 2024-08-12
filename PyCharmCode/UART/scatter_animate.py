import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time

fig, ax = plt.subplots()
x = np.array([0])
y = np.array([0])
scatter = ax.scatter(x, y)

def update(frame):
    new_x = np.append(scatter.get_offsets()[:, 0], frame)
    new_y = np.append(scatter.get_offsets()[:, 1], np.sin(frame))
    scatter.set_offsets(np.c_[new_x, new_y])
    ax.relim()
    ax.autoscale_view()
    time.sleep(1)
    return scatter,

ani = FuncAnimation(fig, update, frames=np.linspace(0, 10, 100), interval=100, blit=True)
plt.show()
