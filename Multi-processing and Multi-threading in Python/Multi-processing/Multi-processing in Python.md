# Multi-processing in Python

## Basic Implementations

* Using `os.fork()` function

  ```python
  import os
  
  print(f'Process (os.getpid()) start...')
  pid = os.fork()  # 操作系统把当前进程(父进程)复制一份(称为子进程)
  # os.fork()函数调用一次, 返回两次: 父进程中返回创建的子进程的ID, 子进程中返回0
  if pid != 0:
      print(f'I ({os.getpid()}) just created a child process {pid}.')
  else:
      print(f'I am child process ({os.getpid()}) and my parent is {os.getppid()}.')
  
  # Output:
  # Process (15918) start...
  # I (15918) just created a child process (15919).
  # I am child process (15919) and my parent is 15918.
  
  ```

* Using `multiprocessing` module

  * Create subprocesses using `Process`

    ```python
    from multiprocessing import Process
    
    
    def run_process(name: str) -> None:
        """
        Dummy task to be run within a process.
        :param name: str
        :return: None
        """
        print(f"Running child process '{name}' ({os.getpid()})")
    
    
    print(f'Parent process {os.getpid()}')
    p = Process(target=run_process, args=('test',))
    print('Child process starting...')
    p.start()
    p.join()
    print('Child process ends.')
    print('Parent process ends.')
    
    # Output:
    # Parent process 16623
    # Child process starting...
    # Running child process 'test' (16624)
    # Child process ends.
    # Parent process ends.
  ```
    
  * Create a <u>pool</u> of subprocesses using `Pool` and `Pool.apply()` method, `Pool.map()` method, `Pool.imap()` method or `Pool.imap_unordered()` method
    
      ```python
      import os
      import random
      import time
      from multiprocessing import Pool
      
      
      def long_time_task(name: str) -> float:
          """
          Dummy long task to be run within a process.
          :param name: str
          :return: float
          """
          print(f"Running task '{name}' ({os.getpid()})...")
          start = time.time()
          time.sleep(random.random() * 3)
          end = time.time()
          time_elapsed = end - start
          print(f"Task '{name}' runs {time_elapsed:.2f} seconds.")
          return time_elapsed
      
      
      print(f'Parent process {os.getpid()}')
      with Pool(4) as pool:  # 开启一个4个进程的进程池
          # 在进程池中执行一个任务
          # pool.apply(func=long_time_task, args=(f'Some Task'))  # Will block here
      
          # 在进程池中concurrently执行多个相同的任务, 只是参数不同
          start = time.time()
          # results = pool.map(
          #     func=long_time_task, iterable=map(lambda x: f'Task-{x}', range(5))
          # )  # Will block here
          total_running_time = 0
          # for result in pool.imap(
          #     func=long_time_task, iterable=map(lambda x: f'Task-{x}', range(5))
          # ):  # Lazy version of pool.map()
          #     total_running_time += result
          for result in pool.imap_unordered(
              func=long_time_task, iterable=map(lambda x: f'Task-{x}', range(5))
          ):  # Lazy, unordered version of pool.map()
              total_running_time += result
          pool.close()  # 调用close()之后就不能再添加新的任务了
          pool.join()
          print(f'Theoretical total running time: {total_running_time:.2f} seconds.')
          end = time.time()
          print(f'Actual running time: {end - start:.2f} seconds.')
      print('All subprocesses done.')
      
      # Output:
      # Parent process 9727
      # Running task 'Task-0' (9728)...
      # Running task 'Task-1' (9729)...
      # Running task 'Task-2' (9730)...
      # Running task 'Task-3' (9731)...
      # Task 'Task-0' runs 0.23 seconds.
      # Running task 'Task-4' (9728)...
      # Task 'Task-3' runs 0.44 seconds.
      # Task 'Task-4' runs 1.39 seconds.
      # Task 'Task-1' runs 1.90 seconds.
      # Task 'Task-2' runs 1.89 seconds.
      # Theoretical total running time: 5.85 seconds.
      # Actual running time: 1.95 seconds.
      # All subprocesses done.
      ```
      
      ***
      
      **Multi-processing + Async  (Subprocess [Coroutine])**
      
      -> 把coroutine包在subprocess中
      
      *创建一个process pool (subprocesses), 在其中放入async的task (coroutine), 参见`multiprocessing_async.py`*
      
      ***

* Using `subprocess` module to create non-self-defined subprocesses

  ```python
  import subprocess

  print('$ nslookup www.python.org')
  r = subprocess.call(['nslookup', 'www.python.org'])
  # 相当于在command line中输入 nslookup www.python.org
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
  # 相当于在command line中输入 nslookup
  p = subprocess.Popen(
      ['nslookup'],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
  )
  output, _ = p.communicate(b'set q=mx\npython.org\nexit\n')
  # 相当于再在command line中输入
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
  ```

<br>

## Communication between Processes

* Through a pipe, creating two `multiprocessing.connection.Connection` objects on both ends of the pipe

  ```python
  from multiprocessing import Pipe, Process
  from multiprocessing.connection import Connection
  
  
  def write_process(conn: Connection) -> None:
      """
      Process to write data to pipe through the given connection.
      :param conn: Connection
      :return: None
      """
      print('Child process writing to the pipe...')
      conn.send([42, None, 'Hello'])
      conn.close()
  
  
  parent_conn, child_conn = Pipe()
  
  p = Process(target=write_process, args=(child_conn,))
  p.start()
  
  print(f'Parent process reading from pipe... {parent_conn.recv()}')
  
  p.join()
  
  # Output:
  # Child process writing to the pipe...
  # Parent process reading from pipe... [42, None, 'Hello']
  ```

* Through `multiprocessing.Queue`

  ```python
  import random
  import time
  from multiprocessing import Process, Queue
  from typing import List
  
  
  def producer_process(q: Queue, urls: List[str]) -> None:
      """
      Producer process to write data to the given message queue.
      :param q: Queue
      :param urls: list[str]
      :return: None
      """
      print('Producer process starts writing...')
      for url in urls:
          q.put(url)
          print(f'[Producer Process] Put {url} to the queue')
          time.sleep(random.random())
  
  
  def consumer_process(q: Queue) -> None:
      """
      Consumer process to get data from the given message queue.
      :param q: Queue
      :return: None
      """
      print('Consumer process starts reading...')
      while True:
          url = q.get(block=True)
          print(f'[Consumer Process] Get {url} from the queue')
  
  
  q = Queue()
  producer1 = Process(target=producer_process, args=(q, ['url1', 'url2', 'url3']))
  producer2 = Process(target=producer_process, args=(q, ['url4', 'url5']))
  consumer = Process(target=consumer_process, args=(q,))
  
  producer1.start()
  producer2.start()
  consumer.start()
  
  producer1.join()
  producer2.join()
  
  # Since there is an infinite loop in consumer_process, we need to manually force
  # it to stop.
  time.sleep(3)  # Make sure the consumer has finished consuming the values
  consumer.terminate()
  
  # Output:
  # Producer process starts writing...
  # [Producer Process] Put url1 to the queue
  # Producer process starts writing...
  # [Producer Process] Put url4 to the queue
  # Consumer process starts reading...
  # [Consumer Process] Get url1 from the queue
  # [Consumer Process] Get url4 from the queue
  # [Producer Process] Put url5 to the queue
  # [Consumer Process] Get url5 from the queue
  # [Producer Process] Put url2 to the queue
  # [Consumer Process] Get url2 from the queue
  # [Producer Process] Put url3 to the queue
  # [Consumer Process] Get url3 from the queue
  ```
  * Don't make too many trips back and forth

    Instead, do significant work in one trip

  * Don't send or receive a lot of data at one time

