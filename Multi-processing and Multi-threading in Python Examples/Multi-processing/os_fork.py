#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test module to create processes using the native os.fork() function.
"""

__author__ = 'Ziang Lu'

import os


def main():
    print(f'Process (os.getpid()) start...')
    pid = os.fork()  # 操作系统把当前进程(父进程)复制一份(称为子进程)
    # os.fork()函数调用一次, 返回两次: 父进程中返回创建的子进程的ID, 子进程中返回0
    if pid != 0:
        print(f'I ({os.getpid()}) just created a child process {pid}.')
    else:
        print(
            f'I am child process ({os.getpid()}) and my parent is '
            f'{os.getppid()}.'
        )


if __name__ == '__main__':
    main()


# Output:
# Process (15918) start...
# I (15918) just created a child process (15919).
# I am child process (15919) and my parent is 15918.
