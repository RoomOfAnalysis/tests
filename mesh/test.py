#!/usr/bin/env python3
"""
@author:Harold
@file: mesh.py
@time: 18/09/2019
"""

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import pandas as pd


def load_3d_pt_cloud_data(path_name: str) -> np.array:
    # https://stackoverflow.com/questions/13187778/convert-pandas-dataframe-to-numpy-array
    # https://pandas.pydata.org/pandas-docs/version/0.24.0rc1/api/generated/pandas.Series.to_numpy.html
    return pd.read_csv(path_name, dtype=np.float32, delimiter=r'[\t\s]', header=None).to_numpy()


def load_3d_pt_cloud_data_with_delimiter(path_name: str, delimiter: str) -> np.array:
    return pd.read_csv(path_name, dtype=np.float32, delimiter=delimiter, header=None).to_numpy()


fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(411, projection='3d')

# Make data.
data = load_3d_pt_cloud_data_with_delimiter('ism_train_cat_normal_mesh.txt', r"\s+")

print(data.shape)

# ax.plot_trisurf(X, Y, Z, linewidth=0.2, antialiased=True)

poly3d = [[data[i, j * 3:j * 3 + 3] for j in range(3)] for i in range(data.shape[0])]
fc = ["crimson" if i % 2 else "gold" for i in range(data.shape[0])]
mesh = Poly3DCollection(poly3d, facecolors=fc, linewidths=0.1, alpha=0.1)
ax.add_collection3d(mesh)
# ax.set_xlim(-30, 0)
# ax.set_ylim(20, 50)
# ax.set_zlim(20, 70)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
# elev -> y, azim -> z
ax.view_init(45, 0)

axx = fig.add_subplot(412, projection='3d')
axx.scatter(data[:, 0], data[:, 1], data[:, 2], color='blue')
axx.set_xlabel("x")
axx.set_ylabel("y")
axx.set_zlabel("z")
axx.view_init(45, 0)

normal_data = load_3d_pt_cloud_data_with_delimiter('ism_train_cat_normal.txt', r"\s+")
X, Y, Z, U, V, W= normal_data[:, 0], normal_data[:, 1], normal_data[:, 2], normal_data[:, 3], normal_data[:, 4], normal_data[:, 5]

bx = fig.add_subplot(413, projection='3d')
bx.scatter(X, Y, Z, color='red')
bx.quiver(X, Y, Z, U, V, W)
bx.set_xlabel("x")
bx.set_ylabel("y")
bx.set_zlabel("z")
bx.view_init(45, 0)

original_data = load_3d_pt_cloud_data_with_delimiter('ism_train_cat.txt', r"\s+")
x, y, z = original_data[:, 0], original_data[:, 1], original_data[:, 2]

cx = fig.add_subplot(414, projection='3d')
cx.scatter(x, y, z, color='black')
cx.set_xlabel("x")
cx.set_ylabel("y")
cx.set_zlabel("z")
cx.view_init(45, 0)

plt.show()
