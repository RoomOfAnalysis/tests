from kthread import KThread
import time
import threading


class Timeout(Exception):
    """function run timeout"""


def timeout(seconds):
    """timeout wrapper func, if wrapped func not return in input timeout, it throws above Timeout exception"""
    def timeout_decorator(func):
        def _new_func(oldfunc, result, oldfunc_args, oldfunc_kwargs):

            result.append(oldfunc(*oldfunc_args, **oldfunc_kwargs))

        def _(*args, **kwargs):

            result = []

            new_kwargs = {  # create new args for _new_func, because we want to get the func return val to result list

                'oldfunc': func,

                'result': result,

                'oldfunc_args': args,

                'oldfunc_kwargs': kwargs

            }

            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)

            thd.start()

            thd.join(seconds)  # join(timeout) is for this thread blocked to wait its sub-thread timeout seconds

            alive = thd.isAlive()  # isAlive() to check if sub-thread timeouts after timeout seconds

            thd.kill()  # kill the child thread

            if alive:
                # raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                try:

                    raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
                finally:
                    return u'function run too long, timeout %d seconds.' % seconds

            else:

                return result[0]

        _.__name__ = func.__name__

        _.__doc__ = func.__doc__

        return _

    return timeout_decorator


if __name__ == '__main__':
    @timeout(1)
    def process_num(num):
        num_add = num + 1
        time.sleep(3)
        return str(threading.current_thread()) + ": " + str(num) + "-> " + str(num_add)
    start = time.time()
    print(process_num(1))
    print("time cost: ", time.time() - start, "s")
