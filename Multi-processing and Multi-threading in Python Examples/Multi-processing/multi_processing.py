#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to create processes using multiprocessing module.
"""

__author__ = 'Ziang Lu'

import os
import random
import subprocess
import time
from multiprocessing import Pool, Process, Queue


def run_process(name: str) -> None:
    """
    Dummy task to be run within a process
    :param name: str
    :return: None
    """
    print(
        "Running child process '{name}' ({pid})".format(name=name,
                                                        pid=os.getpid())
    )


def long_time_task(name: str) -> None:
    """
    Dummy long task to be run within a process.
    :param name: str
    :return: Nones
    """
    print("Running task '{name}' ({pid})...".format(name=name, pid=os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print("Task '{}' runs {.2}f seconds.".format(name, end - start))


def write(q: Queue) -> None:
    """
    Writes messages to the given queue.
    :param q: Queue
    :return: None
    """
    print('Process to write ({pid}})'.format(pid=os.getpid()))
    for c in ['A', 'B', 'C']:
        print('Putting {} to queue...'.format(c))
        q.put(c)
        time.sleep(random.random())


def read(q: Queue) -> None:
    """
    Reads messages from the given queue.
    :param q: Queue
    :return: None
    """
    print('Process to read ({pid})'.format(pid=os.getpid()))
    while True:
        val = q.get(block=True)
        print('Get %s from queue' % val)


def main():
    # Create subprocesses using Process
    print('Parent process {pid}'.format(pid=os.getpid()))
    p = Process(target=run_process, args=('test',))
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process ends.')
    print()

    # Output:
    # Parent process 16623
    # Child process will start.
    # Running child process 'test' (16624)
    # Child process ends.

    # Create many subprocesses using Pool
    print('Parent process {pid}'.format(pid=os.getpid()))
    pool = Pool(4)  # 开启4个进程
    for i in range(5):  # 设置5个任务
        pool.apply_async(func=long_time_task, args=(i,))
    pool.close()  # 调用close()之后就不能再添加新的进程(任务)了
    print('Waiting for all subprocesses done...')
    pool.join()
    print('All subprocesses done')
    print()

    # Output:
    # Parent process 16623
    # Waiting for all subprocesses done...
    # Running task '0' (16625)
    # Running task '1' (16626)
    # Running task '2' (16627)
    # Running task '3' (16628)
    # Task '2' runs 0.14 seconds.
    # Running task '4' (16627)
    # Task '4' runs 0.65 seconds.
    # Task '3' runs 1.50 seconds.
    # Task '1' runs 2.58 seconds.
    # Task '0' runs 2.97 seconds.
    # All subprocesses done
    # (注意由于只开启了4个进程, 却有5个任务, 则task 4只能等待某个进程处理完其任务之后才能在该
    # 进程上执行)

    # Create non-self-defined subprocesses using subprocess module
    print('$ nslookup www.python.org')
    r = subprocess.call(['nslookup', 'www.python.org'])
    # 相当于在命令行中输入 nslookup www.python.org
    print('Exit code:', r)
    print()

    # Output:
    # $ nslookup www.python.org
    # Server:         137.99.203.20
    # Address:        137.99.203.20#53
    #
    # Non-authoritative answer:
    # www.python.org  canonical name = python.map.fastly.net.
    # Name:   python.map.fastly.net
    # Address: 151.101.208.223
    #
    # Exit code: 0

    # Non-self-defined subprocesses might need input
    print('$ nslookup')
    # 相当于在命令行中输入 nslookup
    p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = p.communicate(b'set q=mx\npython.org\nexit\n')
    # 相当于再在命令行中输入
    # set q=mx
    # python.org
    # exit
    print(output.decode('utf-8'))
    print('Exit code:', p.returncode)
    print()

    # Output:
    # $ nslookup
    # Server:         137.99.203.20
    # Address:        137.99.203.20#53
    #
    # Non-authoritative answer:
    # python.org      mail exchanger = 50 mail.python.org
    #
    # Authoratative answers can be found from:
    #
    #
    # Exit code: 0

    # Create Queue objects to realize communcation among processes
    q = Queue()
    p_w = Process(target=write, args=(q,))
    p_r = Process(target=read, args=(q,))
    p_w.start()
    p_r.start()
    p_w.join()
    # 由于read()中是无穷循环, 无法join()等其结束, 而必须要强制终止
    p_r.terminate()

    # Output:
    # Process to write (16631)
    # Putting A to queue...
    # Process to read (16632)
    # Get A from queue
    # Putting B to queue...
    # Get B from queue
    # Putting C to queue...
    # Get C from queue


if __name__ == '__main__':
    main()
