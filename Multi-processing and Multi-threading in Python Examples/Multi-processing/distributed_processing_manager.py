#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed processing: distribute multiple processes to multiple machines.

Task manager module.
"""

__author__ = 'Ziang Lu'

import random
from multiprocessing.managers import BaseManager
from queue import Queue

# 创建发送任务的queue和接受结果的queue
task_queue = Queue()
result_queue = Queue()


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
# 通过ServerQueueManager封装来获取task_queue和result_queue
task_q = server_manager.get_task_queue()
result_q = server_manager.get_result_queue()
# 设置任务
for _ in range(10):
    n = random.randint(0, 10000)
    print(f'Put task ID {n}...')
    task_q.put(n)


# Output:
# Put task ID 6894...
# Put task ID 3637...
# Put task ID 6674...
# Put task ID 8438...
# Put task ID 3889...
# Put task ID 5283...
# Put task ID 8245...
# Put task ID 5281...
# Put task ID 9235...
# Put task ID 3551...


# 从result_q读取任务结果
print('Getting results...')
for _ in range(10):
    r = result_q.get(timeout=10)  # Will block here and wait for getting results
    print(f'Result: {r}')
# 关闭manager
server_manager.shutdown()


# Output:
# Getting results...
# Result: 6894 * 6894 = 47527236
# Result: 3637 * 3637 = 13227769
# Result: 6674 * 6674 = 44542276
# Result: 8438 * 8438 = 71199844
# Result: 3889 * 3889 = 15124321
# Result: 5283 * 5283 = 27910089
# Result: 8245 * 8245 = 67980025
# Result: 5281 * 5281 = 27888961
# Result: 9235 * 9235 = 85285225
# Result: 3551 * 3551 = 12609601
