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
        Dummy task to be run within a process
        :param name: str
        :return: None
        """
        print(f"Running child process '{name}' ({os.getpid()})")
    
    
    print(f'Parent process {os.getpid()}')
    p = Process(target=run_process, args=('test',))
    print('Child process will start.')
    p.start()
    p.join()
    print('Child process ends.')
    print()
    
    # Output:
    # Parent process 16623
    # Child process will start.
    # Running child process 'test' (16624)
    # Child process ends.
    ```

    * Create a <u>pool</u> of subprocesses using `Pool` and `Pool.apply_async()` method or `Pool.imap_unordered()` method

      ```python
      import os
      import random
      import time
      from multiprocessing import Pool
      from typing import Tuple
      
      import requests
      
      
      def long_time_task(name: str) -> None:
          """
          Dummy long task to be run within a process.
          :param name: str
          :return: Nones
          """
          print(f"Running task '{name}' ({os.getpid()})...")
          start = time.time()
          time.sleep(random.random() * 3)
          end = time.time()
          print(f"Task '{name}' runs {end - start:.2f} seconds.")
      
      
      # with Pool.apply_async() method
      print(f'Parent process {os.getpid()}')
      pool = Pool(4)  # 开启4个进程
      for i in range(5):  # 设置5个任务
          pool.apply_async(func=long_time_task, args=(i,))
      pool.close()  # 调用close()之后就不能再添加新的进程(任务)了
      print('Waiting for all subprocesses done...')
      pool.join()
      print('All subprocesses done.')
      print()
      
      # Output:
      # Parent process 16623
      # Waiting for all subprocesses done...
      # Running task '0' (16625)
      # Running task '1' (16626)
      # Running task '2' (16627)
      # Running task '3' (16628)
      # Task '2' runs 0.14 seconds.
      # Running task '4' (16627)
      # Task '4' runs 0.65 seconds.
      # Task '3' runs 1.50 seconds.
      # Task '1' runs 2.58 seconds.
      # Task '0' runs 2.97 seconds.
      # All subprocesses done.
      
      
      sites = [
          'http://www.cisco.com',
          'http://www.cnn.com',
          'http://www.facebook.com',
          'http://www.jpython.org',
          'http://www.pypy.org',
          'http://www.python.org',
          'http://www.twitter.com',
          'https://www.yahoo.com/'
      ]
      
      
      def site_size(url: str) -> Tuple[str, int]:
          """
          Returns the page size in bytes of the given URL.
          :param url: str
          :return: tuple(str, int)
          """
          response = requests.get(url)
          # Note that since we want to use Pool.imap_unordered() method, even though
          # we know the order of the input URLs, the order of the results is
          # arbitrary, so we need to return the input URL as well to know which input
          # URL corresponds to which result
          return url, len(response.content)
      
      
      # with Pool.imap_unordered() method
      pool = Pool(5)
      for result in pool.imap_unordered(site_size, sites):
          print(result)
      
      # Output:
      # ('http://www.pypy.org', 5539)
      # ('http://www.cisco.com', 81777)
      # ('http://www.cnn.com', 1724737)
      # ('http://www.python.org', 50131)
      # ('http://www.facebook.com', 554929)
      # ('http://www.jpython.org', 19210)
      # ('http://www.twitter.com', 232134)
      # ('https://www.yahoo.com/', 521603)
      ```

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
  p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

```python
import random
import time
from multiprocessing import Process, Queue
from typing import List


def write_process(q: Queue, urls: List[str]) -> None:
    """
    Process to write data to the given message queue.
    :param q: Queue
    :param urls: list[str]
    :return: None
    """
    print('Process starts writing...')
    for url in urls:
        q.put(url)
        print(f'Put {url} to the queue [Write Process]')
        time.sleep(random.random())


def read_process(q: Queue) -> None:
    """
    Process to get data from the given message queue.
    :param q: Queue
    :return: None
    """
    print('Process starts reading...')
    while True:
        url = q.get(block=True)
        print(f'Get {url} from the queue [Read Process]')


q = Queue()
writer1 = Process(target=write_process, args=(q, ['url1', 'url2', 'url3']))
writer2 = Process(target=write_process, args=(q, ['url4', 'url5']))
reader = Process(target=read_process, args=(q,))

writer1.start()
writer2.start()
reader.start()

writer1.join()
writer2.join()

# Since there is an infinite loop in read_process, we need to manually force it
# to stop.
reader.terminate()

# Output:
# Process starts writing...
# Put url1 to the queue [Write Process]
# Put url4 to the queue [Write Process]
# Process starts reading...
# Get url1 from the queue [Read Process]
# Get url4 from the queue [Read Process]
# Put url5 to the queue [Write Process]
# Get url5 from the queue [Read Process]
# Put url2 to the queue [Write Process]
# Get url2 from the queue [Read Process]
# Put url3 to the queue [Write Process]
# Get url3 from the queue [Read Process]
```

- Don't make too many trips back and forth

  Instead, do significant work in one trip

- Don't send or receive a lot of data at one time

