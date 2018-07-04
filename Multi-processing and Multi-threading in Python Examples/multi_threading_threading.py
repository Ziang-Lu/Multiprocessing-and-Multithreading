#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to create threads using threading module.
"""

__author__ = 'Ziang Lu'

import threading
import time


def loop() -> None:
    thread_name = threading.current_thread().name
    print('Running thread %s...' % thread_name)
    n = 1
    while n < 5:
        print('thread %s >>> %d' % (thread_name, n))
        time.sleep(1)
        n += 1
    print('Thread %s ends.' % thread_name)


def process_thread(local, std_name: str) -> None:
    local.student = std_name  # 在ThreadLocal中绑定当前线程对应的student
    greet_student(local)


def greet_student(local) -> None:
    student = local.student  # 从ThreadLocal中获取当前线程关联的student
    print('Hello, %s (in %s)' % (student, threading.current_thread().name))


def main():
    # Create subthreads using threading.Thread
    thread_name = threading.current_thread().name
    print('Running thread %s...' % thread_name)
    th = threading.Thread(target=loop, name='LoopThread')
    th.start()
    th.join()
    print('Thread %s ends.' % thread_name)
    print()

    # Output:
    # Running thread MainThread...
    # Running thread LoopThread...
    # thread LoopThread >>> 1
    # thread LoopThread >>> 2
    # thread LoopThread >>> 3
    # thread LoopThread >>> 4
    # Thread LoopThread ends.
    # Thread MainThread ends.

    # Use threading.ThreadLocal to encapsulate data in each thread
    # ThreadLocal可以看做一个{线程: 线程属性dict}的dict, 用于管理线程内部的数据
    # ThreadLocak封装了使用线程作为key检索对应的属性dict, 再使用属性名作为key检索属性值的细
    # 节
    thread_local = threading.local()
    th_a = threading.Thread(target=process_thread, args=(thread_local, 'Alice'),
                            name='Thread-A')
    th_b = threading.Thread(target=process_thread, args=(thread_local, 'Bob'),
                            name='Thread-B')
    th_a.start()
    th_b.start()
    th_a.join()
    th_b.join()

    # Output:
    # Hello, Alice (in Thread-A)
    # Hello, Bob (in Thread-B)


if __name__ == '__main__':
    main()


# 注意:
# Python的线程虽然是真正的线程, 但解释器执行代码时, 有一个GIL锁 (Global Interpreter Lock)
# 任何Python线程执行前, 必须先获得GIL, 然后, 每执行100条字节码, 解释器就自动释放GIL锁, 让别
# 的线程有机会执行
# 所以, 多线程在Python中只能交替进行
# (即使100个线程跑在100核CPU上, 也只能用到1个核 => 不可能通过多线程实现并发(parallelism))
# 但由于每个进程有各自独立的GIL, 可以通过多进程实现并发
