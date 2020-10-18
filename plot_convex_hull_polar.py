#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: plot_convex_hull_polar.py
@time: 2020/10/18
"""

from matplotlib import pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.collections import PolyCollection

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='polar')

# generating some data:
C = np.random.rand(30) * 15 + 40
h = np.random.rand(30) * 15 + 290
h = np.radians(h)  # convert values of the angle from degrees to radians

# following scipy example
points = np.array([p for p in zip(h, C)])
hull = ConvexHull(points)
for i in [points[hull.vertices, :]]:
    print(i)

ax1.scatter(h, C, s=5, marker='o', color='b')

# adding the convex hull to ax1 as a PolyCollection:
ax1.add_collection(PolyCollection(
    [points[hull.vertices, :]],
    edgecolors='r',
    facecolors='w',
    linewidths=2,
    zorder=-1,
))

ax1.set_rmax(60)

plt.show()
