import select
import sys
import time

while True:
    print("waiting for IO...")
    r, w, e = select.select([sys.stdin, sys.stdout], [sys.stdin, sys.stdout], [])
    time.sleep(1)
    for x in r:
        print('r = ', x)
    for x in w:
        print('w = ', x)
    for x in e:
        print('e = ', x)
