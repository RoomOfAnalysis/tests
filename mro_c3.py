#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: mro_c3.py
@time: 2020/08/26
"""


def c3(cls):
    if len(cls.__bases__) == 1:
        return [cls, cls.__bases__]
    else:
        # recursion
        base_list = [c3(base) for base in cls.__bases__]
        base_list.append(list(cls.__bases__))
        return [cls] + merge(base_list)


def merge(base_list):
    if base_list:
        for mro in base_list:
            for cls in mro:
                for cmp in base_list:
                    if cls in cmp[1:]:
                        break
                else:
                    next_merge = []
                    for mro_ in base_list:
                        if cls in mro_:
                            mro_.remove(cls)
                            if mro_:
                                next_merge.append(mro_)
                        else:
                            next_merge.append(mro_)
                    return [cls] + merge(next_merge)
        else:
            raise Exception
    else:
        return []


if __name__ == '__main__':
    class A:
        pass

    class B:
        pass

    class C:
        pass

    class E(A, B):
        pass

    class F(B, C):
        pass

    class G(E, F):
        pass

    print(c3(G))

    print(G.mro())

'''
all class inherit from object:
mro(E) = [E] + merge(mro(A), mro(B), [A, B])
       = [E] + merge([A, O], [B, O], [A, B])
       = [E, A] + merge([O], [B, O], [B])
       = [E, A, B] + merge([O], [O])
       = [E, A, B, O]

mro(G) = [G] + merge(mro(E), mro(F), [E, F])
       = [G] + merge([E, A, B, O], [F, B, C, O], [E, F])
       = [G, E] + merge([A, B, O], [F, B, C, O], [F])
       = [G, E, A] + merge([B, O], [F, B, C, O], [F])
       = [G, E, A, F] + merge([B, O], [B, C, O])
       = [G, E, A, F, B] + merge([O], [C, O])
       = [G, E, A, F, B, C] + merge([O], [O])
       = [G, E, A, F, B, C, O]
'''