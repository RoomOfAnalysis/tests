#
## benchmark of loop function in python, compiled_python and compiled_pyx

```bash
(venv) ➜  primes git:(master) ✗ make benchmark 
python -m timeit -s 'from primes_python import primes_python' 'primes_python(1000)'
10 loops, best of 3: 25.8 msec per loop
python -m timeit -s 'from primes_python_cy import primes_python_compiled' 'primes_python_compiled(1000)'
100 loops, best of 3: 12.8 msec per loop
python -m timeit -s 'from primes import primes' 'primes(1000)'
100 loops, best of 3: 2.01 msec per loop
python -m timeit -s 'from primes_cpp import primes_cpp' 'primes_cpp(1000)'
100 loops, best of 3: 2.02 msec per loop
```

> The cythonize version of primes_python is 2 times faster than the Python one, without changing a single line of code. The Cython version is 13 times faster than the Python version! What could explain this?
>
> Multiple things:
> - In this program, very little computation happen at each line. So the overhead of the python interpreter is very important. It would be very different if you were to do a lot computation at each line. Using NumPy for example.
> - Data locality. It’s likely that a lot more can fit in CPU cache when using C than when using Python. Because everything in python is an object, and every object is implemented as a dictionary, this is not very cache friendly.
>
> Usually the speedups are between 2x to 1000x. It depends on how much you call the Python interpreter. As always, remember to profile before adding types everywhere. Adding types makes your code less readable, so use them with moderation.
