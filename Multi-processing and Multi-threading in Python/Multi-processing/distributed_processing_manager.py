#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed processing: distribute multiple processes to multiple machines.

Task manager module.
"""

__author__ = 'Ziang Lu'

import random
from multiprocessing import Queue
from multiprocessing.managers import BaseManager

# 创建发送任务的queue和接受结果的queue
task_queue = Queue(maxsize=5)
result_queue = Queue(maxsize=5)


class ServerQueueManager(BaseManager):
    pass


# 给ServerQueueManager注册两个函数来分别返回两个queue
ServerQueueManager.register('get_task_queue', callable=lambda: task_queue)
ServerQueueManager.register('get_result_queue', callable=lambda: result_queue)

# Server端

# 创建manager, 并绑定端口5000, 设置验证码abc
server_manager = ServerQueueManager(address=('', 5000), authkey=b'abc')
# 启动manager
server_manager.start()
print('Server manager started.')
# 通过ServerQueueManager封装来获取task_queue和result_queue
task_q = server_manager.get_task_queue()
result_q = server_manager.get_result_queue()
# 设置任务
for _ in range(10):
    n = random.randint(0, 10000)
    print(f'Put task {n}...')
    task_q.put(n)

# Output:
# Server manager started.
# Put task 8739...
# Put task 5790...
# Put task 474...
# Put task 8122...
# Put task 4101...
# Put task 8863...
# Put task 3944...
# Put task 7217...
# Put task 6542...
# Put task 2097...


# 从result_q读取任务结果
print('Getting results...')
for _ in range(10):
    # Will block here and wait for getting results
    r = result_q.get(timeout=10)
    print(f'Result: {r}')
# 关闭manager
server_manager.shutdown()
print('Server manager exited.')

# Output:
# Getting results...
# Result: 8739 * 8739 = 76370121
# Result: 5790 * 5790 = 33524100
# Result: 474 * 474 = 224676
# Result: 8122 * 8122 = 65966884
# Result: 4101 * 4101 = 16818201
# Result: 8863 * 8863 = 78552769
# Result: 3944 * 3944 = 15555136
# Result: 7217 * 7217 = 52085089
# Result: 6542 * 6542 = 42797764
# Result: 2097 * 2097 = 4397409
# Server manager exited.
