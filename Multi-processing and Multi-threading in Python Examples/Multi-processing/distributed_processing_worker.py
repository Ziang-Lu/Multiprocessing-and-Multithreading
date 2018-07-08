#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed processing: distribute multiple processes to multiple machines.

Task worker module.
"""

import time
from multiprocessing.managers import BaseManager
from queue import Queue


class WorkerQueueManager(BaseManager):
    pass


# 由于WorkerQueueManager只从网络上获取queue, 所以注册时只提供名字
WorkerQueueManager.register('get_task_queue')
WorkerQueueManager.register('get_result_queue')

# Worker端

server_addr = '127.0.0.1'
print('Connecting to server {}...'.format(server_addr))
# 创建manager, 端口和验证码注意与manager.py中保持一致
worker_manager = WorkerQueueManager(address=(server_addr, 5000), authkey=b'abc')
# 连接至服务器
worker_manager.connect()
# 通过WorkerQueueManager封装来获取task_queue和result_queue
task_q = worker_manager.get_task_queue()
result_q = worker_manager.get_result_queue()
# 从task_queue获取任务, 执行任务, 并把结果写入result_queue
for _ in range(10):
    try:
        n = task_q.get(timeout=1)
        print('Running task {n} * {n}...'.format(n=n))
        r = '{n} * {n} = {result}'.format(n=n, result=n * n)
        time.sleep(1)
        result_q.put(r)
    except Queue.Empty:
        print('Task queue is empty.')
print('Worker exits.')


# Output:
# Running task 6894 * 6894...
# Running task 3637 * 3637...
# Running task 6674 * 6674...
# Running task 8438 * 8438...
# Running task 3889 * 3889...
# Running task 5283 * 5283...
# Running task 8245 * 8245...
# Running task 5281 * 5281...
# Running task 9235 * 9235...
# Running task 3551 * 3551...
# Worker exits.
