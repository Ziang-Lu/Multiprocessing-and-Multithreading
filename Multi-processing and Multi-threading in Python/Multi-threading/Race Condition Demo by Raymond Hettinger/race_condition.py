#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo of race condition, amplified by fuzzing technique.
"""

import random
import time
from threading import Thread

# Fizzing is a technique for amplifying race condition to make them more
# visible.
# Basically, define a fuzz() function, which simply sleeps a random amount of
# time if instructed, and then call the fuzz() function before each operation

# Fuzzing setup

FUZZ = True


def fuzz() -> None:
    """
    Fuzzes the program for a random amount of time, if instructed.
    :return: None
    """
    if FUZZ:
        time.sleep(random.random())


# Shared global variable
counter = 0


def worker() -> None:
    """
    :return: None
    """
    global counter
    fuzz()
    old_val = counter  # Read from the global variable
    fuzz()
    counter = old_val + 1  # Write to the global variable
    # Whenever there is read from/write to global variables, there could be race
    # condition.
    # To amplify this race condition to make it more visible, we utilize fuzzing
    # technique as mentioned above.
    fuzz()
    # Note that the built-in print() function is also a "global" resource, and
    # thus could lead to race condition as well
    print(f'The counter is {counter}')
    fuzz()
    print('----------')


print('Starting up')
for _ in range(10):
    Thread(target=worker).start()
    fuzz()
print('Finishing up')
