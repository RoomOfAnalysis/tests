import pynng
import random
import sys
import time
import mmap
import multiprocessing

ipc_address = "ipc:///tmp/abcde"
data_mmfn = "data.txt"
result_mmfn = "result.txt"
N = 1920 * 1080 * 3
R = 1024


def client(n, dm, rm):
    with pynng.Req0(dial=ipc_address) as req:
        ba = (random.getrandbits(8 * n)).to_bytes(n, sys.byteorder)
        try:
            t0 = time.time_ns()
            req.send(b"connect")
            if req.recv() == b"data":
                t1 = time.time_ns()
                dm.write(ba)
                print("write data to mmap", (time.time_ns() - t1) / 10 ** 6, "ms")
                req.send(b"ready")
            if req.recv() == b"result":
                print(len(rm))
                req.send(b"get")
            print("ttl: ", (time.time_ns() - t0) / 10 ** 6, "ms")
        except Exception as e:
            print(e)


def server(addr, n, dm, rm):
    with pynng.Rep0(listen=addr) as rep:
        ba = (random.getrandbits(8 * n)).to_bytes(n, sys.byteorder)
        while True:
            if rep.recv() == b"connect":
                rep.send(b"data")
            if rep.recv() == b"ready":
                print(len(dm))
                t0 = time.time_ns()
                rm.write(ba)
                print("write result to mmap: ", (time.time_ns() - t0) / 10 ** 6, "ms")
                rep.send(b"result")
            if rep.recv() == b"get":
                rep.send(b"data")


if __name__ == '__main__':
    with open(data_mmfn, "wb") as df, open(result_mmfn, "wb") as rf:
        df.truncate(N)
        rf.truncate(R)
    with open(data_mmfn, "r+b") as df, open(result_mmfn, "r+b") as rf:
        with mmap.mmap(df.fileno(), 0) as dm, mmap.mmap(rf.fileno(), 0) as rm:
            sp = multiprocessing.Process(target=server, args=(ipc_address, R, dm, rm))
            sp.start()
            time.sleep(1)
            client(N, dm, rm)
            sp.kill()
