#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to implement synchronous blocking, to address race condition among
threads, using threading.Lock and
threading.Semaphore/threading.BoundedSemaphore.
"""

__author__ = 'Ziang Lu'

import threading
import time

balance = 0

# Lock
lock = threading.Lock()


def thread_func(n: int) -> None:
    """
    Dummy function to be run within a thread.
    :param n: int
    :return: None
    """
    for _ in range(10000000):
        lock.acquire()
        try:
            change_balance(n)
        finally:
            lock.release()  # 确保锁一定会被释放


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


th1 = threading.Thread(target=thread_func, args=(5,))
th2 = threading.Thread(target=thread_func, args=(8,))
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

bounded_sema = threading.BoundedSemaphore(value=2)  # A bounded semaphore with initial value 2


def func() -> None:
    """
    Dummy function.
    :return: None
    """
    thread_name = threading.current_thread().name
    # 请求Semaphore, 成功后计数器-1
    print('{th_name} acquiring semaphore...'.format(th_name=thread_name))
    if bounded_sema.acquire():
        print('{th_name} gets semaphore'.format(th_name=thread_name))
        time.sleep(4)
        # 释放Semaphore, 计数器+1
        bounded_sema.release()


threads = [threading.Thread(target=func) for _ in range(4)]
for th in threads:
    th.start()
for th in threads:
    th.join()


# Output:
# Thread-3 acquiring semaphore...
# Thread-3 gets semaphore
# Thread-4 acquiring semaphore...
# Thread-4 gets semaphore
# Thread-5 gets semaphore
# Thread-6 gets semaphore   # Will block here for 4 seconds, waiting for the semaphore
# Thread-5 gets semaphore
# Thread-6 gets semaphore
