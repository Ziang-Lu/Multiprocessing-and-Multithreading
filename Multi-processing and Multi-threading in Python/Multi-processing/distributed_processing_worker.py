#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed processing: distribute multiple processes to multiple machines.

Task worker module.
"""

import time
from multiprocessing import Queue
from multiprocessing.managers import BaseManager


class WorkerQueueManager(BaseManager):
    pass


# 由于WorkerQueueManager只从网络上获取queue, 所以注册时只提供名字
WorkerQueueManager.register('get_task_queue')
WorkerQueueManager.register('get_result_queue')

# Worker端

server_addr = '127.0.0.1'
# 创建manager, 端口和验证码注意与manager.py中保持一致
worker_manager = WorkerQueueManager(
    address=(server_addr, 5000), authkey=b'abc'
)
# 连接至服务器
print(f'Connecting to server {server_addr}...')
worker_manager.connect()
print('Worker started.')
# 通过WorkerQueueManager封装来获取task_queue和result_queue
task_q = worker_manager.get_task_queue()
result_q = worker_manager.get_result_queue()
# 从task_queue获取任务, 执行任务, 并把结果写入result_queue
for _ in range(10):
    try:
        n = task_q.get(timeout=1)
        print(f'Calculating {n} * {n}...')
        result = f'{n} * {n} = {n * n}'
        time.sleep(1)
        result_q.put(result)
    except Queue.Empty:
        print('Task queue is empty.')
print('Worker exits.')


# Output:
# Connecting to server 127.0.0.1...
# Worker started.
# Calculating 8739 * 8739...
# Calculating 5790 * 5790...
# Calculating 474 * 474...
# Calculating 8122 * 8122...
# Calculating 4101 * 4101...
# Calculating 8863 * 8863...
# Calculating 3944 * 3944...
# Calculating 7217 * 7217...
# Calculating 6542 * 6542...
# Calculating 2097 * 2097...
# Worker exits.
