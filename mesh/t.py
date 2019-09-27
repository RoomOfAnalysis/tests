# !/usr/bin/env python3
"""
@author:Harold
@file: t.py
@time: 19/09/2019
"""

# https://stackoverflow.com/questions/43393162/how-to-plot-3d-triangles-in-matplotlib-with-triangles-verticess-coordinates-9

import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

phi = np.linspace(0, 2 * np.pi, 7)
x = np.cos(phi) + np.sin(phi)
y = -np.sin(phi) + np.cos(phi)
z = np.cos(phi) * 0.12 + 0.7

a = np.zeros((len(phi) - 1, 9))
a[:, 0] = x[:-1]
a[:, 1] = y[:-1]
a[:, 2] = z[:-1]
a[:, 3:6] = np.roll(a[:, 0:3], -1, axis=0)
a[:, 8] = np.ones_like(phi[:-1])
a = np.around(a, 2)
print(a)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

fc = ["crimson" if i % 2 else "gold" for i in range(a.shape[0])]

poly3d = [[a[i, j * 3:j * 3 + 3] for j in range(3)] for i in range(a.shape[0])]

ax.add_collection3d(Poly3DCollection(poly3d, facecolors=fc, linewidths=1))

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)

plt.show()
