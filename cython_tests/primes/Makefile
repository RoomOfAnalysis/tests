setup:
	python setup.py build_ext --inplace

benchmark:

	python -m timeit -s 'from primes_python import primes_python' 'primes_python(1000)'

	python -m timeit -s 'from primes_python_cy import primes_python_compiled' 'primes_python_compiled(1000)'

	python -m timeit -s 'from primes import primes' 'primes(1000)'

	python -m timeit -s 'from primes_cpp import primes_cpp' 'primes_cpp(1000)'
