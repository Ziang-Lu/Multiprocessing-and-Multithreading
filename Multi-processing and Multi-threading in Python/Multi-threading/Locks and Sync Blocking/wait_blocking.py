#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to implement wait blocking to address race condition, using
threading.Condition and threading.Event.
"""

__author__ = 'Ziang Lu'

import time
from threading import Condition, Event, Thread, current_thread

# Condition

product = None  # 商品
condition = Condition()


def producer() -> None:
    while True:
        if condition.acquire():
            global product
            if not product:
                # 生产商品
                print('Producing something...')
                product = 'anything'
                condition.notify()

            condition.wait()
            time.sleep(2)


def consumer() -> None:
    while True:
        if condition.acquire():
            global product
            if product:
                # 消耗商品
                print('Consuming something...')
                product = None
                condition.notify()

            condition.wait()
            time.sleep(2)


prod_thread = Thread(target=producer)
cons_thread = Thread(target=consumer)
prod_thread.start()
cons_thread.start()


# Output:
# Producing something...
# Consuming something...
# Producing something...
# Consuming something...
# ...
