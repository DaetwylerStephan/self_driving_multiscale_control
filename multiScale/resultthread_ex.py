import threading
import numpy as np
from concurrency_tools import ResultThread

def f(a):
    ''' A function that does something... '''
    return a.sum()


##
## Getting Results:
##
a = np.ones((2,), dtype='uint8')

# Our problem:
th = threading.Thread(target=f, args=(a,))
th.start()
th.join()  # We can't access the result of f(a) without redefining f!

# Our solution:
res_th = ResultThread(target=f, args=(a,)).start()
res = res_th.get_result()  # returns f(a)
assert res == 2

##
## Error handling
##
a = 1

# Our problem:
th = threading.Thread(target=f, args=(a,))
th.start()
th.join()
# f(a) raised an unhandled exception. Our parent thread has no idea!

#Our solution:
res_th = ResultThread(target=f, args=(a,)).start()
try:
    res = res_th.get_result()
except AttributeError:
    print("AttributeError was raised in thread!")
else:
    raise AssertionError(
        'We expected an AttributeError to be raised on join!')
print("test")