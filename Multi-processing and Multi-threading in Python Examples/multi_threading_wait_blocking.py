#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to implement wait blocking, to address race condition, using
threading.Condition and threading.Event.
"""

__author__ = 'Ziang Lu'

import threading
import time

# Condition

product = None  # 商品
condition = threading.Condition()


def produce() -> None:
    if condition.acquire():  # 1. 成功获得锁定   [等待池: 空, 锁定池: 空, 已锁定: P]
        while True:
            global product
            if product is None:
                # 生产商品
                print('Producing...')
                product = 'anything'
                # 通知消费者, 商品已生产
                condition.notify()  # 2. 由于等待池为空, 并没有通知任何线程, 且不会释放锁   [等待池: 空, 锁定池: C, 已锁定: P]
                                    # 6. 通知C, C自动调用acquire()来尝试获得锁定(进入锁定池), 但当前线程不会释放锁   [等待池: 空, 锁定池: C, 已锁定: P]

        condition.wait()  # 3. 当前线程进入等待池, 并释放锁   [等待池: P, 锁定池: C, 已锁定: 空]
                          # 4. 接到通知, 自动调用acquire()来尝试获得锁定(进入锁定池)   [等待池: 空, 锁定池: P, 已锁定: C]
                          # 5. 由于C释放了锁, 成功获得锁定   [等待池: C, 锁定池: 空, 已锁定: P]
                          # 7 -> 3
        time.sleep(2)


def consume() -> None:
    if condition.acquire():  # 1. 尝试获得锁定, 同步阻塞在锁定池中   [等待池: 空, 锁定池: C, 已锁定: P]
                             # 3. 由于P释放了锁, 成功获得锁定   [等待池: P, 锁定池: 空, 已锁定: C]
        while True:
            global product
            if product is not None:
                # 消耗商品
                print('Consuming...')
                product = None
                # 通知生产者, 商品已消耗
                condition.notify()  # 4. 通知P, P自动调用acquire()来尝试获得锁定(进入锁定池), 但当前线程不会释放锁   [等待池: 空, 锁定池: P, 已锁定: C]

        condition.wait()  # 5. 当前线程进入等待池, 并释放锁   [等待池: C, 锁定池: P, 已锁定: 空]
                          # 6. 接到通知, 自动调用acquire()来尝试获得锁定(进入锁定池)   [等待池: 空, 锁定池: C, 已锁定: P]
                          # 7 -> 3
        time.sleep(2)


# prod_thread = threading.Thread(target=produce)
# cons_thread = threading.Thread(target=consume)
# prod_thread.start()
# cons_thread.start()


# Output:
# Producing...
# Consuming...
# Producing...
# Consuming...
# ...


# Simple demo

L = None
condition = threading.Condition()


def print_list() -> None:
    if condition.acquire():  # 1. 成功获得锁定   [等待池: 空, 锁定池: 空, 已锁定: P]
        global L
        while L is None:
            condition.wait()  # 2. 当前进程进入等待池, 并释放锁   [等待池: P, 锁定池: S C, 已锁定: 空]
                              # 4. 接到通知, 自动调用acquire()来尝试获得锁定(进入锁定池)   [等待池: 空, 锁定池: P S, 已锁定: C]
                              # 5. 由于C释放了锁, 成功获得锁定   [等待池: 空, 锁定池: S, 已锁定: P]
        for i in L:
            print(i, end=' ')
        print()
        condition.release()  # 6. 释放锁, 同时线程结束   [等待池: 空, 锁定池: S, 已锁定: 空]


def set_list() -> None:
    if condition.acquire():  # 1. 尝试获得锁定, 同步阻塞在锁定池中   [等待池: 空, 锁定池: S, 已锁定: P]
                             # 2. 由于P释放了锁, 成功获得锁定   [等待池: P, 锁定池: C, 已锁定: S]
        global L
        while L is None:
            condition.wait()  # 3. 当前进程进入等待池, 并释放锁   [等待池: P S, 锁定池: C, 已锁定: 空]
                              # 4. 接到通知, 自动调用acquire()来尝试获得锁定(进入锁定池)   [等待池: 空, 锁定池: P S, 已锁定: C]
                              # 6. 由于P释放了锁, 成功获得锁定   [等待池: 空, 锁定池: 空, 已锁定: S]
        for i in range(len(L) - 1, -1, -1):
            L[i] = 1
        condition.release()  # 7. 释放锁, 同时线程结束   [等待池: 空, 锁定池: 空, 已锁定: 空]


def create_list() -> None:
    if condition.acquire():  # 1. 尝试获得锁定, 同步阻塞在锁定池中   [等待池: 空, 锁定池: S C, 已锁定: P]
                             # 3. 由于S释放了锁, 成功获得锁定   [等待池: P S, 锁定池: 空, 已锁定: C]
        global L
        if L is None:
            L = [0] * 10
            condition.notify_all()  # 4. 通知P S, P S自动调用acquire尝试获取锁定(进入锁定池), 但当前线程不会释放锁   [等待池: 空, 锁定池: P S, 已锁定: C]
        condition.release()  # 5. 释放锁, 同时线程结束   [等待池: 空, 锁定池: P S, 已锁定: 空]


print_thread = threading.Thread(target=print_list)
set_thread = threading.Thread(target=set_list)
create_thread = threading.Thread(target=create_list)
threads = [print_thread, set_thread, create_thread]
for th in threads:
    th.start()
for th in threads:
    th.join()
print(L)


# Output:
# 0 0 0 0 0 0 0 0 0 0
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


# Event
# 本质上是一个简化版的Condition; 只是Event没有锁, 无法使线程进入同步阻塞状态
# 管理一个初始为false的flag, 当调用set()方法时设置为true, 调用clear()方法时重置为false
# wait()方法阻塞当前线程至等待阻塞状态, 直到其他线程调用set()使flag为true, 唤醒全部等待的线程

event = threading.Event()


def func() -> None:
    thread_name = threading.current_thread().name
    print('%s waiting for event...' % thread_name)
    event.wait()  # 阻塞当前线程至等待阻塞状态, 直到其他线程调用set()使flag为true, 唤醒当前线程

    # 被唤醒后直接进入运行状态 (没有锁定池)
    print('%s receives event.' % thread_name)


th1 = threading.Thread(target=func)
th2 = threading.Thread(target=func)
th1.start()
th2.start()

print('%s sets event.' % threading.current_thread().name)
event.set()  # 发送事件通知

th1.join()
th2.join()


# Output:
# Thread-6 waiting for event...
# Thread-7 waiting for event...
# MainThread sets event.
# Thread-7 receives event.
# Thread-6 receives event.
