#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple demo of solution of race conditions with (atomic) message queue.
Note that the race conditions in this demo are also amplified by fuzzing
technique

In order to be away with race conditions, we need to
1. Ensure an explicit ordering of the operations (on the shared resources)
   All operations (on the shared resources) must be executed in the same order
   they are received.
   => To ensure this, we simply put the operations (on one shared resource) in a
      single thread.
2. Restrict access to the shared resource
   Only one operation can access the shared resource at the same time. During
   the period of access, no other operations can read or change its value.

Specifically for solution with (atomic) message queue,
1. Each shared resource shall be accessed in exactly its own thread.
2. All communications with that thread shall be done using an atomic message
   queue.
"""

import random
import time
from threading import Thread
from queue import Queue

##### Fuzzing technique #####

FUZZ = False


def fuzz() -> None:
    """
    Fuzzes the program for a random amount of time, if instructed.
    :return: None
    """
    if fuzz:
        time.sleep(random.random())


##### Daemon thread for print() access & Atomic message queue for print() #####

# Note that the built-in print() function is a "global" resource, and thus could
# lead to race condition
# Therefore, as instructed above, accessing the print() function should be
# handled in exactly its own thread, which should be a daemon thread. (=> 1)

# All communications with the print()-access daemon thread shall be done using
# an atomic message queue. (=> 2)
print_queue = Queue()  # Atomic message queue used for the print()-access daemon thread


def print_manager() -> None:
    """
    Daemon thread function that uses an atomic message queue to communicate with
    the external world, and has exclusive right to access the print() function.
    :return: None
    """
    while True:
        fuzz()
        stuff_to_print = print_queue.get()
        for line in stuff_to_print:
            fuzz()
            print(line)
        fuzz()
        # Mark the task as done
        print_queue.task_done()


# Create and start the print()-access daemon thread
print_daemon_thread = Thread(target=print_manager,
                             name='print()-access Daemon Thread')
print_daemon_thread.daemon = True
print_daemon_thread.start()


##### Daemon thread for "counter" & Atomic message queue for "counter" #####

counter = 0
# As instructed above, accessing the "counter" global variable should be handled
# in exactly its own thread, which should be a daemon thread. (=> 1)

# All communications with the "counter"-access daemon thread shall be done using
# an atomic message queue. (=> 2)
# Atomic message queue used for the "counter"-access daemon thread
counter_queue = Queue()


def counter_manager() -> None:
    """
    Daemon thread function that uses an atomic message queue to communicate with
    the external world, and has exclusive right to access the "counter" global
    variable.
    :return: None
    """
    while True:
        global counter
        fuzz()
        old_val = counter
        fuzz()
        increment = counter_queue.get()
        fuzz()
        counter = old_val + increment
        fuzz()
        # Send a message to the print()-access atomic message queue in order to
        # print the "counter" value
        print_queue.put([f'The counter value is {counter}', '----------'])
        fuzz()
        # Mark the task as done
        counter_queue.task_done()


# Create and start the "counter"-access daemon thread
counter_daemon_thread = Thread(target=counter_manager,
                               name='Counter-access Daemon Thread')
counter_daemon_thread.daemon = True
counter_daemon_thread.start()


##### Actual workers #####


def worker() -> None:
    """
    Thread function that increments "counter" by 1.
    This is done by sending a message to the "counter"-access atomic message
    queue.
    :return: None
    """
    fuzz()
    counter_queue.put(1)


print_queue.put(['Starting up'])

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
# By now, it is guaranteed that 10 messages has been sent to the
# "counter"-access atomic message queue, but the tasks haven't necesserily been
# done yet.

# Note that since the "counter"-access queue is a daemon thread and never ends,
# we cannot join it
# Instead, we can join the atomic message queue itself, which waits until all
# the tasks has been marked as done.
counter_queue.join()

print_queue.put(['Finishing up'])
print_queue.join()  # Same reason as above
