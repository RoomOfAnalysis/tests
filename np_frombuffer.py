import timeit

# https://stackoverflow.com/questions/7044044/an-efficient-way-of-making-a-large-random-bytearray

if __name__ == '__main__':
    #'''
    T = 10 ** 6
    t = timeit.timeit('np.frombuffer(ba, dtype=np.uint8)',
                      setup='import random, sys\n'
                            'import numpy as np\n'
                            #'N = 1920 * 1080 * 3\n'
                            #'N = 100\n'
                            'N = 3 * 1024 * 1024\n'
                            'ba = (random.getrandbits(8 * N)).to_bytes(N, sys.byteorder)',
                      number=T)
    print(t, "us")
    '''
    T = 10 ** 3
    t = timeit.timeit('np.fromstring(ba, dtype=np.uint8)',
                      setup='import random, sys\n'
                            'import numpy as np\n'
                            'N = 1920 * 1080 * 3\n'
                            'ba = (random.getrandbits(8 * N)).to_bytes(N, sys.byteorder)',
                      number=T)
    print(t, "ms")
    '''
