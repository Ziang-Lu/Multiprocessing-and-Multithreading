#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to create threads using threading module.
"""

__author__ = 'Ziang Lu'

import threading
import time
from threading import local, Thread


def loop() -> None:
    """
    Loop to be run within a thread.
    :return: None
    """
    thread_name = threading.current_thread().name
    print('Running thread {th_name}...'.format(th_name=thread_name))
    n = 1
    while n < 5:
        print('thread {} >>> {}'.format(thread_name, n))
        time.sleep(1)
        n += 1
    print('Thread {th_name} ends.'.format(th_name=thread_name))


def process_thread(local_: local, std_name: str) -> None:
    """
    Processes a thread and put the student of the current thread to the
    ThreadLocal.
    :param local_: local
    :param std_name: str
    :return: None
    """
    local_.student = std_name  # 在ThreadLocal中绑定当前thread对应的student
    greet_student(local_)


def greet_student(local_: local) -> None:
    """
    Greets the student of the current thread.
    :param local_: local
    :return:
    """
    student = local_.student  # 从ThreadLocal中获取当前thread关联的student
    print(
        'Hello, {std} (in {th_name})'.format(
            std=student, th_name=threading.current_thread().name
        )
    )


def main():
    # Create subthreads using threading.Thread
    thread_name = threading.current_thread().name
    print('Running thread %s...' % thread_name)
    th = Thread(target=loop, name='LoopThread')
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
    # ThreadLocal可以看做一个{thread: thread属性dict}的dict, 用于管理thread内部的数据
    # ThreadLocal封装了使用thread作为key检索对应的属性dict, 再使用属性名作为key检索属性值的细节
    thread_local = threading.local()
    th_a = Thread(target=process_thread, args=(thread_local, 'Alice'),
                  name='Thread-A')
    th_b = Thread(target=process_thread, args=(thread_local, 'Bob'),
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
# Python的thread虽然是真正的thread, 但解释器执行代码时, 有一个GIL锁 (Global Interpreter Lock)
# 任何Python thread执行前, 必须先获得GIL, 然后, 每执行100条字节码, 解释器就自动释放GIL锁, 让别的thread有机会执行
# (Python 2.x)
# 所以, multi-threading在Python中只能交替进行
# (即使100个thread跑在100核CPU上, 也只能用到1个核 => 不可能通过multi-threading实现parallelism)
# 但由于每个process有各自独立的GIL, 可以通过multi-processing实现concurrency
