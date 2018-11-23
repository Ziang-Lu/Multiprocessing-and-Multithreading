#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo of solution of race conditions with locks.
Note that the race conditions in this demo are also amplified by fuzzing
technique

In order to be away with race conditions, we need to
1. Ensure an explicit ordering of the operations (on the shared resources)
   All operations (on the shared resources) must be executed in the same order
   they are received.
2. Restrict access to the shared resource
   Only one operation can access the shared resource at the same time. During
   the period of access, no other operations can read or change its value.

Specifically for solution with locks,
2. All accesses to the shared resource shall be done using its own lock.
"""

import random
import time
from threading import Condition, Thread

##### Fuzzing technique #####

FUZZ = False


def fuzz() -> None:
    """
    Fuzzes the program for a random amount of time, if instructed.
    :return: None
    """
    if fuzz:
        time.sleep(random.random())


##### Locks for print()-access & "counter"-access #####

# All accesses to the shared resource shall be done using its own lock. (=> 2)
print_lock = Condition()  # Lock for print()-access

counter = 0

counter_lock = Condition()  # Lock for "counter"-access


def worker() -> None:
    """
    Thread function that increments "counter" by 1.
    :return: None
    """
    global counter
    # Lock on the "counter"-access lock
    with counter_lock:
        fuzz()
        old_val = counter
        fuzz()
        counter = old_val + 1
        # Lock on the print()-access lock
        with print_lock:
            fuzz()
            print(f'The counter value is {counter}')
            fuzz()
            print('----------')


# Lock on the print()-access lock
with print_lock:
    print('Starting up')

# Create and start 10 worker threads
worker_threads = []
for _ in range(10):
    worker_thread = Thread(target=worker)
    worker_threads.append(worker_thread)
    worker_thread.start()
    fuzz()
# Join the 10 worker threads
for worker_thread in worker_threads:
    worker_thread.join()
    fuzz()

# Lock on the print()-access lock
with print_lock:
    print('Finishing up')
