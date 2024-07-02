from __future__ import print_function

import sys
import threading
import time
from time import sleep
import _thread as thread



def cdquit(fn_name):
    # print to stderr, unbuffered in Python 2.
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    thread.interrupt_main() # raises KeyboardInterrupt


def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, cdquit, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)

            finally:
                timer.cancel()
            return result
        return inner
    return outer


def ejecucion_segundos(s):
    def fun(fn):
        def wrapper(*args,**kwargs):
            timer = threading.Timer(0,fn,args=[*args])
            time.sleep(s)
            timer.cancel()
        return wrapper()
    return fun

@ejecucion_segundos(2)
def prueba():
    i = 0
    while True:
        i += 1
        print(i)
    return "2"

print(prueba())

print("HOla")