'''
import timeit


s = """\
from abc import ABC, abstractmethod


class Foo(ABC):
    @abstractmethod
    def sum(self):
        raise NotImplementedError

    def sum_2(self):
        pass


class Bar(Foo):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def sum(self):
        return self.a + self.b

    def sum_2(self):
        return self.a + self.b
"""


if __name__ == '__main__':
    s1 = """\
        s = Bar(1, 2)
        s.sum()"""

    s2 = """\
        s = Bar(1, 2)
        s.sum_2()"""
    print(timeit.timeit(stmt=s1, setup=s, number=1000000))
    print(timeit.timeit(stmt=s2, setup=s, number=1000000))
'''


from abc import ABC, abstractmethod
import dis


class Foo(ABC):
    @abstractmethod
    def sum(self):
        raise NotImplementedError

    def sum_2(self):
        pass


class Bar(Foo):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def sum(self):
        return self.a + self.b

    def sum_2(self):
        return self.a + self.b


if __name__ == '__main__':
    dis.dis(Bar(1, 2).sum)
    dis.dis(Bar(1, 2).sum_2)
