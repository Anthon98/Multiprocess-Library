import time
import logging
import multiprocessing as mp

from functools import partial
from multiprocessing import Process, Lock, Value, Manager, Pool
from itertools import repeat

logging.getLogger().setLevel(logging.INFO)

''' 
This tool lets you have multiple functions that
share the same value, using pool.map with multiprocessing.
Yes, you can assign ex. 4 simultaneous workers per function!
'''

# EDIT: Interestingly, this doesn't speed up the time it takes to add +1 to a shared value, most likely due to how locking works.


def add_func_1(total, lock):
    logging.info("First")
    for i in range(10):
        lock.acquire()
        total.value += 1
        logging.info(total.value)
        lock.release()


def add_func_2(total, lock):
    logging.info("Second")
    for i in range(10):
        lock.acquire()
        total.value += 1
        logging.info(total.value)
        lock.release()


def smap(f):
    return f()


if __name__ == '__main__':
    # pool.map needs manager.Value & manager.Lock to work.
    manager = Manager()
    total = manager.Value('i', 0)
    lock = manager.Lock()
    pool = Pool()

    # Complete our func arguments for pool map.
    partials = [
        partial(add_func_1, total=total, lock=lock),
        partial(add_func_2, total=total, lock=lock)
    ]

    # How many processes do we want per function?:
    per_func_mp = 3

    # Create N processes per func:
    processes_iter = [x for item in partials for x in repeat(item, per_func_mp)]

    # Trick is to call smap which returns the func iterator.
    a = pool.map(smap, processes_iter)

    logging.info("Value: %s | Runtime: %s" % (total.value, time.perf_counter()))
