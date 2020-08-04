#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: check_default_arg_passed.py
@time: 2020/08/04
"""


import inspect


class CheckDefault(object):
    def __init__(self, func, **defaults):
        self.func = func
        self.defaults = defaults

    def __call__(self, **kwargs):
        for key in self.defaults:
            if key in kwargs:
                # pass as default
                if kwargs[key] == self.defaults[key]:
                    return True
                # not
                else:
                    return False
            else:
                kwargs[key] = self.defaults[key]
        return self.func(**kwargs)


if __name__ == '__main__':
    def f(a, b=0, preferred='False'):
        pass
    check_f = CheckDefault(f, preferred='False')
    #print(check_f(preferred='False'))
    #print(check_f(preferred='True'))

    def g(a, b=0, preferred='False'):
        print(g.__defaults__)
        args = inspect.getfullargspec(g)
        print(args[0])
        if preferred in g.__defaults__:
            print("not passed")
        else:
            print("passed")
    g(1, 2)
    g(1, 2, 'True')

