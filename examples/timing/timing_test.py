import time


def accurate_delay(delay):
    ''' Function to provide accurate time delay in millisecond
    '''
    _ = time.perf_counter() + delay/1000
    while time.perf_counter() < _:
        pass


delay = 10
t_start = time.perf_counter()
print('Wait for {:.0f} ms. Start: {:.5f}'.format(delay, t_start))

accurate_delay(delay)

t_end = time.perf_counter()
print('End time: {:.5f}. Delay is {:.5f} ms'.
      format(t_end, 1000*(t_end - t_start)))

sum = 0
ntests = 1000
for _ in range(ntests):
    t_start = time.perf_counter()
    accurate_delay(delay)
    t_end = time.perf_counter()
    print('Test completed: {:.2f}%'.format(_/ntests * 100), end='\r', flush=True)
    sum = sum + 1000*(t_end - t_start) - delay

print('Average difference in time delay is {:.5f} ms.'.format(sum/ntests))