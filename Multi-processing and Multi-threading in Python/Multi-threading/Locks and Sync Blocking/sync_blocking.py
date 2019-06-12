#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to implement synchronous blocking to address race condition among
threads, using threading.Lock and
threading.Semaphore/threading.BoundedSemaphore.
"""

__author__ = 'Ziang Lu'

import time
from threading import BoundedSemaphore, Lock, Semaphore, Thread, current_thread

balance = 0

# Lock
lock = Lock()


def thread_func(n: int) -> None:
    """
    Dummy function to be run within a thread.
    :param n: int
    :return: None
    """
    for _ in range(10000000):
        # Note that Lock objects can be used in a traditional way, i.e., via
        # acquire() and release() methods, but it can also simply be used as a
        # context manager, as a syntax sugar
        with lock:
            change_balance(n)


def change_balance(n: int) -> None:
    """
    Changes the balance.
    :param n: int
    :return: None
    """
    global balance
    balance += n
    balance -= n
    # 先存后取, 效果应该为无变化


th1 = Thread(target=thread_func, args=(5,))
th2 = Thread(target=thread_func, args=(8,))
th1.start()
th2.start()
th1.join()
th2.join()
print(balance)


# Output:
# 0


# Semaphore
# 管理一个内置的计数器, 每当调用acquire()时-1, 调用release()时+1
# 计数器不能小于0; 当计数器为0时, acquire()将阻塞线程至同步锁定状态, 直到其他线程调用
# release()

# 注意: 同时acquire semaphore的线程仍然可能会有race condition

# BoundedSemaphore
# 在Semaphore的基础上, 不允许计数器超过initial value (设置上限)

# A bounded semaphore with initial value 2
bounded_sema = BoundedSemaphore(value=2)


def func() -> None:
    """
    Dummy function.
    :return: None
    """
    th_name = current_thread().name
    # 请求Semaphore, 成功后计数器-1
    print(f'{th_name} acquiring semaphore...')
    # Note that BoundedSemaphore objects can be used in a traditional way, i.e.,
    # via acquire() and release() methods, but it can also simply be used as a
    # context manager, as a syntax sugar
    with bounded_sema:  # 释放Semaphore的时候, 计数器+1
        print(f'{th_name} gets semaphore')
        time.sleep(4)


threads = [Thread(target=func) for _ in range(4)]
for th in threads:
    th.start()
for th in threads:
    th.join()


# Output:
# Thread-3 acquiring semaphore...
# Thread-3 gets semaphore
# Thread-4 acquiring semaphore...
# Thread-4 gets semaphore
# Thread-5 acquiring semaphore...
# Thread-6 acquiring semaphore...   # Will block here for 4 seconds, waiting for the semaphore
# Thread-5 gets semaphore
# Thread-6 gets semaphore
