#!/usr/bin/env python3
"""
@author:Harold
@file: primes.py
@time: 09/07/2019
"""

# http://www.pythontutor.com/visualize.html#code=def%20_odd_iter%28%29%3A%0A%20%20%20%20n%20%3D%201%0A%20%20%20%20while%20True%3A%0A%20%20%20%20%20%20%20%20n%20%3D%20n%20%2B%202%0A%20%20%20%20%20%20%20%20yield%20n%0A%20%20%20%20%20%20%20%20%0Adef%20_not_divisible%28n%29%3A%0A%20%20%20%20def%20inner%28x%29%3A%0A%20%20%20%20%20%20%20%20print%28'%25d%20div%20%25d'%20%25%20%28x,%20n%29%29%0A%20%20%20%20%20%20%20%20return%20x%20%25%20n%0A%20%20%20%20return%20inner%0A%20%20%20%20%0Adef%20primes%28%29%3A%0A%20%20%20%20yield%202%0A%20%20%20%20it%20%3D%20_odd_iter%28%29%0A%20%20%20%20%0A%20%20%20%20while%20True%3A%0A%20%20%20%20%20%20%20%20n%20%3D%20next%28it%29%0A%20%20%20%20%20%20%20%20yield%20n%0A%20%20%20%20%20%20%20%20it%20%3D%20filter%28_not_divisible%28n%29,%20it%29%0A%20%20%20%20%20%20%20%20%0Adef%20main%28%29%3A%0A%20%20%20%20for%20n%20in%20primes%28%29%3A%0A%20%20%20%20%20%20%20%20if%20n%20%3C%20100%3A%0A%20%20%20%20%20%20%20%20%20%20%20%20print%28n%29%0A%20%20%20%20%20%20%20%20else%3A%0A%20%20%20%20%20%20%20%20%20%20%20%20break%0A%0Amain%28%29&cumulative=false&curInstr=93&heapPrimitives=nevernest&mode=display&origin=opt-frontend.js&py=3&rawInputLstJSON=%5B%5D&textReferences=false


def _odd_iter():
    n = 1
    while True:
        n = n + 2
        yield n


def _not_divisible(n):
    def inner(x):
        print('%d div %d' % (x, n))
        return x % n

    return inner


def primes():
    yield 2
    it = _odd_iter()

    while True:
        n = next(it)
        yield n
        it = filter(_not_divisible(n), it)


def main():
    for n in primes():
        if n < 100:
            print(n)
        else:
            break


main()
