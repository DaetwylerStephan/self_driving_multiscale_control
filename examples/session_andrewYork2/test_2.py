import time

t0= time.perf_counter()
for i in range(1000):
    time.sleep(0.000)

tend = time.perf_counter()-t0
print(tend)