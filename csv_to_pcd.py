#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: csv_to_pcd.py
@time: 2021/02/01
"""

import pandas as pd
import open3d as o3d
import numpy as np

data = pd.read_csv('xcsv',
                   delimiter=',', skiprows=15).to_numpy()

print(data.shape)
# print(data)

data1 = np.zeros(shape=(data.shape[0] * data.shape[1], 3))
print(data1.shape)
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        data1[i * data.shape[1] + j] = [i, j, data[i][j]]  # row * cols + col

# print(data1)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(data1)
o3d.visualization.draw_geometries_with_editing([pcd])
# o3d.io.write_point_cloud("x.ply", pcd)

