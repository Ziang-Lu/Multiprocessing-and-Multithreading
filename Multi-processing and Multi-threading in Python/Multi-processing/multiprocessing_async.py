#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multiprocessing module (especially, process pool) can work asynchronously, i.e.,
we can assign asynchronous tasks into a process pool.
"""

__author__ = 'Ziang Lu'

import os
import random
import time
from multiprocessing import Pool


def long_time_task(name: str) -> float:
    """
    Dummy long task to be run within a process.
    :param name: str
    :return: float
    """
    print(f"Running task '{name}' ({os.getpid()})...")
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    time_elapsed = end - start
    print(f"Task '{name}' runs {time_elapsed:.2f} seconds.")
    return time_elapsed


print(f'Parent process {os.getpid()}')
with Pool(4) as pool:  # 开启一个4个进程的进程池
    start = time.time()
    # 在进程池中执行多个任务, 但是在主进程中是async的
    results = [
        pool.apply_async(func=long_time_task, args=(f'Task-{i}',))
        for i in range(5)
    ]  # Will NOT block here
    pool.close()  # 调用close()之后就不能再添加新的任务了

    # Since apply_async() method is asynchronous (non-blocking), by now the
    # tasks in the process pool are still executing, but in this main process,
    # we have successfully proceeded to here.
    total_running_time = 0
    for result in results:  # AsyncResult
        total_running_time += result.get(timeout=10)  # Returns the result when it arrives

    print(f'Theoretical total running time: {total_running_time:.2f} seconds.')
    end = time.time()
    print(f'Actual running time: {end - start:.2f} seconds.')
print('All subprocesses done.')

# Output:
# Parent process 10161
# Running task 'Task-0' (10162)...
# Running task 'Task-1' (10163)...
# Running task 'Task-2' (10164)...
# Running task 'Task-3' (10165)...
# Task 'Task-2' runs 1.08 seconds.
# Running task 'Task-4' (10164)...
# Task 'Task-3' runs 1.43 seconds.
# Task 'Task-0' runs 2.69 seconds.
# Task 'Task-1' runs 2.72 seconds.
# Task 'Task-4' runs 2.07 seconds.
# Theoretical total running time: 10.00 seconds.
# Actual running time: 3.18 seconds.
# All subprocesses done.
