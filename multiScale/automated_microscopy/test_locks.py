# example of a mutual exclusion (mutex) lock for processes
from time import sleep
from random import random
from multiprocessing import Process
from multiprocessing import Lock


# work function
def task(lock, identifier, value):
    # acquire the lock
    with lock:
        print(f'>process {identifier} got the lock, sleeping for {value}')
        sleep(value)

def run():
    # create the shared lock
    lock = Lock()
    # create a number of processes with different sleep times
    processes = [Process(target=task, args=(lock, i, random())) for i in range(10)]
    # start the processes
    for process in processes:
        process.start()
    # wait for all processes to finish
    for process in processes:
        process.join()

# entry point
if __name__ == '__main__':
    run()