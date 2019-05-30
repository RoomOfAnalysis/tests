#!/usr/bin/env python3
"""
@author:Harold
@file: setup.py
@time: 30/05/2019
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(["primes.pyx",  # Cython code file with primes() function
                           "primes_cpp.pyx",  # Cython code file with primes_cpp() function and compiled to cpp
                           "primes_python_cy.py"],  # Python code file with primes_python_compiled() function
                          annotate=True),  # enables generation of the html annotation file
)
