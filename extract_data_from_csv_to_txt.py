#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: extract_data_from_csv.py
@time: 2021/05/26
"""

import numpy as np
import argparse
import os
import re


def file_exists(x):
    if not os.path.exists(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

def dir_exists(x):
    dir = os.path.dirname(x)
    if not os.path.exists(dir):
        raise argparse.ArgumentTypeError("{0} does not exist".format(dir))
    return x

def rows_valid(x):
    x = int(x)
    if x < 1 and x != -1:
        raise argparse.ArgumentError("input rows number {0} invalid".format(x))
    return x

def to_float(value):
    try:
        return float(re.sub('[^.\-\d]', '', value))
    except ValueError:
        return float('nan')

def xy_calibration(x):
    x = to_float(x)
    if x <= 0:
        raise argparse.ArgumentError("xy_calibration {0} invalid".format(x))
    return x

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from csv and store into txt')
    parser.add_argument('-f', '--file', dest='filepath', required=True, nargs=1, 
                        type=file_exists,
                        help='filepath')
    parser.add_argument('-r', '--rows', dest='rows', default=[-1, -1], nargs=2,
                        type=rows_valid,
                        help='rows number range (default [-1, -1] means all rows)')                    
    parser.add_argument('-c', '--cols', dest='cols', default=[-1, -1], nargs=2,
                        type=rows_valid,
                        help='cols number range (default [-1, -1] means all cols)')
    parser.add_argument('-o', '--out', dest='outfilepath', required=True, nargs=1, 
                        type=dir_exists,
                        help='output filepath')
    parser.add_argument('-v', '--convert', dest='convert', action='store_true',
                        help='convert to 2d or 3d array')
    parser.add_argument('-xy', '--xy_calibration', dest='xy_calibration', default=1.0, nargs='?',
                        type=xy_calibration,
                        help='when use convertion on xy, require xy calibration (length/pixel)')
    parser.add_argument('-z', '--z_calibration', dest='z_calibration', default=1.0, nargs='?',
                        type=xy_calibration,
                        help='when use convertion on z, require z calibration (length/unit)')
    args = parser.parse_args()

    file = os.path.abspath(args.filepath[0])
    print("rows number {0} ([-1, -1] means all rows)".format(args.rows))
    print("cols number {0} ([-1, -1] means all cols)".format(args.cols))
    rows = args.rows
    cols = args.cols
    max_rows = None
    if (rows != [-1, -1]):
        rows[0] -= 1 # start from 1 in csv
        max_rows = rows[1] - rows[0]
    if cols == [-1, -1]:
        data = np.genfromtxt(file, delimiter=',', skip_header=rows[0], max_rows=1, dtype = 'str', encoding=None)
        cols[0] = 0
        cols[1] = data.shape[0] # 1d array (cols,)
    else:
        cols[0] -= 1 # start from 1 in csv
    data = np.genfromtxt(file, delimiter=',', skip_header=rows[0], max_rows=max_rows, usecols=tuple(range(cols[0], cols[1])), dtype=None, converters={ i : to_float for i in range(cols[0], cols[1]) }, encoding=None)

    r, c = data.shape
    n_data = np.empty([r*c, 3], dtype=float)

    # if need convert to 3d array
    if cols[1] - cols[0] > 3 and args.convert:
        print("xy_calibration {0}".format(args.xy_calibration))
        print("z_calibration {0}".format(args.z_calibration))
        i = 0
        j = 0
        for x, y in zip(np.nditer(data), range(r*c)):
            n_data[y] = [i * args.xy_calibration, j * args.xy_calibration, x * args.z_calibration]
            j += 1
            if j == c:
                i += 1
                j = 0
    # or need convert to 2d array
    elif cols[1] - cols[0] == 2 and args.convert:
        print("xy_calibration {0}".format(args.xy_calibration))
        print("z_calibration {0}".format(args.z_calibration))
        n_data = data[:, [0, 1]]
        n_data[:, 0] *= args.xy_calibration
        n_data[:, 1] *= args.z_calibration
    else:
        n_data = data

    np.savetxt(os.path.abspath(args.outfilepath[0]), n_data, delimiter=' ', fmt='%.6f')
