#!/usr/bin/env python3
"""
@author:Harold
@file: poisson.py
@time: 27/09/2019
"""

from pypoisson import poisson_reconstruction
from ply_from_array import points_normals_from, ply_from_array

filename = "ism_train_cat_normal.txt"
output_file = "ism_train_cat_normal_recon.ply"

points, normals = points_normals_from(filename)

faces, vertices = poisson_reconstruction(points, normals, depth=10)

ply_from_array(vertices, faces, output_file=output_file)
