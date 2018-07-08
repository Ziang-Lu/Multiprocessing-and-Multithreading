#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to create threads using _thread module (now deprecated).
"""

__author__ = 'Ziang Lu'

import _thread
import time


def print_time(thread_name: str, delay: float) -> None:
    count = 0
    while count < 3:
        time.sleep(delay)
        count += 1
        print(
            '{th_name}: {time}'.format(th_name=thread_name,
                                       time=time.ctime(time.time())
        ))


def main():
    try:
        _thread.start_new_thread(print_time, ('Thread-1', 2))
        _thread.start_new_thread(print_time, ('Thread-2', 4))
    except:
        print('Error: Cannot start the thread')

    while True:
        pass


if __name__ == '__main__':
    main()


# Output:
# Thread-1: Wed Jan 31 18:03:49 2018
# Thread-2: Wed Jan 31 18:03:51 2018
# Thread-1: Wed Jan 31 18:03:51 2018
# Thread-1: Wed Jan 31 18:03:53 2018
# Thread-2: Wed Jan 31 18:03:55 2018
# Thread-2: Wed Jan 31 18:03:59 2018
