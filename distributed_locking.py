#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed locking mechanism using Redis.

We can use Redis's single-threaded feature to
1. Implement a naive distributed lock
   Simple but imperfect
   => In NOT so high-concurrent scenarios, this works just fine.
2. Use a third-party library
   Complex but perfect
   => Works for high-concurrent scenarios
"""

import redis
from redlock import MultipleRedlockException, Redlock

LOCK_KEY = 'lock'


def set_up() -> None:
    """
    Stock setup.
    :return: None
    """
    r = redis.Redis()

    r.set('stock', 10)


def lightning_order() -> None:
    """
    Lightning order.
    :return: None
    """
    r = redis.Redis()

    # Use a "lock" key as the lock
    # => We need to set the value of the "lock" key to be unique for every
    #    client, so that when releasing the lock, we know whether this lock has
    #    been automatically released.
    client_id = r.client_id()
    result = r.setnx(LOCK_KEY, client_id)
    while not result:  # If not acquiring the lock, block here
        result = r.setnx(LOCK_KEY, client_id)

    # Acquired the lock
    # => We need to set an expire time for "lock", so that eventually this lock
    #    will be released.
    r.expire(LOCK_KEY, 30)
    # But how do we set the expire time?
    # => Estimate the execution time of the business codes, and set the expire
    #    time to be longer than it, so make sure the client who acquired the
    #    lock has enough time to execute the business codes.
    try:
        # Business codes
        remaining = int(r.get('stock'))
        if remaining > 0:
            r.set('stock', str(remaining - 1))
            print(f'Deducted stock, {remaining - 1} remaining')
        else:
            print('Failed to deduct stock')
        # PROBLEM:
        # If our web application goes down during the business codes, the
        # "finally" part still won't get executed, meaning that the client who
        # acquired the lock may NOT be able to release it, leading to a deadlock
        # forever.
        # => We need to set an expire time for "lock", so that eventually this
        #    lock will be released.
    finally:
        # In case that the business codes may raise an exception, we should
        # release the lock in a "finally", by deleting "lock" key.
        # r.delete('lock')

        # PROBLEM:
        # What if the execution time of the business codes exceeds the expire
        # time for "lock"?
        # In this case, the lock is "released" before the execution of the
        # business codes, and some other client is able to acquire the same
        # lock, which is unsafe.
        # => We need to set the value of the "lock" key to be unique for every
        #    client, so that when releasing the lock, we know whether this lock has
        #    been automatically released.
        lock_val = r.get(LOCK_KEY)
        if lock_val != client_id:
            raise Exception('Business codes timed out.')
        r.delete(LOCK_KEY)


def lightning_order_with_redlock() -> None:
    """
    Lightning order with Redlock algorithm.
    :return: None
    """
    r = redis.Redis()

    dlm = Redlock([{
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }, ])  # Stands for "distributed lock manager"

    lock = None
    try:
        # Try to acquire the lock
        lock = dlm.lock(LOCK_KEY, 30000)  # If not acquiring the lock, block here
        # Business codes
        remaining = int(r.get('stock'))
        if remaining > 0:
            r.set('stock', str(remaining - 1))
            print(f'Deducted stock, {remaining - 1} remaining')
        else:
            print('Failed to deduct stock')
    except MultipleRedlockException as e:
        print(e)
    finally:
        # Release the lock
        dlm.unlock(lock)
