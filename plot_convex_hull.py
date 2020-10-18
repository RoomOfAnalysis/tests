#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: plot_convex_hull.py
@time: 2020/10/18
"""

import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

points = np.random.rand(30, 2)   # 30 random points in 2-D
hull = ConvexHull(points)

plt.plot(points[:, 0], points[:, 1], 'o')
cent = np.mean(points, 0)
pts = []
for pt in points[hull.simplices]:
    pts.append(pt[0].tolist())
    pts.append(pt[1].tolist())

pts.sort(key=lambda p: np.arctan2(p[1] - cent[1],
                                  p[0] - cent[0]))
pts = pts[0::2]  # Deleting duplicates
pts.insert(len(pts), pts[0])
k = 1
color = 'green'
poly = Polygon(k*(np.array(pts) - cent) + cent,
               facecolor=color, alpha=0.2)
poly.set_capstyle('round')
plt.gca().add_patch(poly)

plt.show()
