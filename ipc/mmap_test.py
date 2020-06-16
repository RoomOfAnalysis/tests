import mmap

if __name__ == '__main__':
    with open("test.txt", "wb") as f:
        f.write(b"hello world\n")
    with open("test.txt", "r+b") as f:
        with mmap.mmap(f.fileno(), 0) as m:
            print(m.readline())
