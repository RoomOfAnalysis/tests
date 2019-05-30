#!/usr/bin/env python3
"""
@author:Harold
@file: setup.py
@time: 30/05/2019
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("hello_world.pyx")
)
