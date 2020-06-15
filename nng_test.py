import pynng
import random
import sys
import time

ipc_address = "ipc:///tmp/abcde"
tcp_address = "tcp://127.0.0.1:4321"


def main():
    for N in [100, 3 * 1024 * 1024, 1920 * 1080 * 3]:
        ba = (random.getrandbits(8 * N)).to_bytes(N, sys.byteorder)
        with pynng.Rep0(listen=ipc_address) as rep, pynng.Req0(dial=ipc_address) as req:
            t0 = time.time_ns()
            req.send(ba)
            rep.send(rep.recv())
            print((time.time_ns() - t0) / 10 ** 6, "ms")


if __name__ == "__main__":
    main()
