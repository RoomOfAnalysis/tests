#!/usr/bin/env python
# -*- coding:utf-8 _*-  
"""
@author:Harold
@license: MIT Licence
@file: get_func_s_class.py
@time: 2020/07/27
"""

import inspect


# reference:
# https://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3?noredirect=1&lq=1


def get_class_that_defined_method(meth):
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth) and getattr(meth, '__self__') is not None and getattr(meth.__self__, '__class__')):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__')  # handle special descriptor objects


if __name__ == '__main__':
    class A:
        def a(self):
            pass
    print(get_class_that_defined_method(A.a))
