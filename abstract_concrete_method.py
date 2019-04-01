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

# 0.629273695
# 0.623510672
'''


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
    

# 0 LOAD_FAST                0 (self)
# 2 LOAD_ATTR                0 (a)
# 4 LOAD_FAST                0 (self)
# 6 LOAD_ATTR                1 (b)
# 8 BINARY_ADD
# 10 RETURN_VALUE

# 0 LOAD_FAST                0 (self)
# 2 LOAD_ATTR                0 (a)
# 4 LOAD_FAST                0 (self)
# 6 LOAD_ATTR                1 (b)
# 8 BINARY_ADD
# 10 RETURN_VALUE

'''

'''
import timeit
s = """\
from abc import ABC, abstractmethod


class Foo1(ABC):
    @abstractmethod
    def sum(self):
        raise NotImplementedError
    
    
class Foo2(ABC):
    def sum(self):
        pass
    

class Bar1(Foo1):
    def __init__(self, a, b):
        self.a, self.b = a, b
        
    def sum(self):
        return self.a + self.b
    
    
class Bar2(Foo2):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def sum(self):
        return self.a + self.b
"""


if __name__ == '__main__':
    s1 = """\
        s = Bar1(1, 2)
        s.sum()"""

    s2 = """\
        s = Bar2(1, 2)
        s.sum()"""
    print(timeit.timeit(stmt=s1, setup=s, number=1000000))
    print(timeit.timeit(stmt=s2, setup=s, number=1000000))
    
# 0.627910772
# 0.624692045
'''
    
    
from abc import ABC, abstractmethod
import dis


class Foo1(ABC):
    @abstractmethod
    def sum(self):
        raise NotImplementedError


class Foo2(ABC):
    def sum(self):
        pass


class Bar1(Foo1):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def sum(self):
        return self.a + self.b


class Bar2(Foo2):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def sum(self):
        return self.a + self.b


if __name__ == '__main__':
    dis.dis(Bar1(1, 2).sum)
    dis.dis(Bar2(1, 2).sum)

'''
0 LOAD_FAST                0 (self)
2 LOAD_ATTR                0 (a)
4 LOAD_FAST                0 (self)
6 LOAD_ATTR                1 (b)
8 BINARY_ADD
10 RETURN_VALUE

0 LOAD_FAST                0 (self)
2 LOAD_ATTR                0 (a)
4 LOAD_FAST                0 (self)
6 LOAD_ATTR                1 (b)
8 BINARY_ADD
10 RETURN_VALUE
'''
