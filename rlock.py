#!/usr/bin/env python3
"""
@author:Harold
@file: rlock.py.py
@time: 17/04/2019
"""

# reference:
# https://stackoverflow.com/questions/16567958/when-and-how-to-use-pythons-rlock
# https://docs.python.org/3/library/threading.html#threading.Lock
# https://docs.python.org/3/library/threading.html#threading.RLock

from threading import Event, RLock, Thread, Lock


def guardian_func():
    while True:
        WebFacingInterface.guardian_allow_access.clear()
        # ResourceManager.resource_lock.acquire()
        WebFacingInterface.resource_modifying_method()
        WebFacingInterface.guardian_allow_access.wait()
        # ResourceManager.resource_lock.release()


class ResourceManager:
    resource_lock = Lock()  # Lock()
    # Lock() can only acquire and release once but RLock() can be acquired multiple times

    def update_this(self):
        if self.resource_lock.acquire(False):
            try:
                print('Lock Acquired By This')
                return True
            finally:
                self.resource_lock.release()
        else:
            return False

    def update_that(self):
        if self.resource_lock.acquire(False):
            try:
                print('Lock Acquired By That')
                return True
            finally:
                self.resource_lock.release()
        else:
            return False


class WebFacingInterface:
    guardian_allow_access = Event()
    resource_guardian = Thread(None, guardian_func, 'Guardian', [])
    resource_manager = ResourceManager()

    @classmethod
    def resource_modifying_method(cls):
        cls.guardian_allow_access.set()
        # cls.resource_manager.resource_lock.acquire()
        cls.resource_manager.update_this()
        cls.resource_manager.update_that()
        # cls.resource_manager.resource_lock.release()


if __name__ == '__main__':
    # WebFacingInterface.resource_modifying_method()
    # guardian_func()
    WebFacingInterface.resource_guardian.run()
