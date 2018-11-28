# Multi-threading in Python

## Basic Implementations

* Using `threading` module

  * Normal implementation

    ```python
    import time
    from threading import Thread, current_thread, local
    
    
    def loop() -> None:
        """
        Loop to be run within a thread.
        :return: None
        """
        th_name = current_thread().name
        print(f'Running thread {th_name}...')
        n = 1
        while n < 5:
            print(f'thread {th_name} >>> {n}')
            time.sleep(1)
            n += 1
        print(f'Thread {th_name} ends.')
    
    
    th_name = current_thread().name
    print(f'Running thread {th_name}...')
    th = Thread(target=loop, name='LoopThread')
    th.start()
    th.join()
    print(f'Thread {th_name} ends.')
    print()
    
    # Output:
    # Running thread MainThread...
    # Running thread LoopThread...
    # thread LoopThread >>> 1
    # thread LoopThread >>> 2
    # thread LoopThread >>> 3
    # thread LoopThread >>> 4
    # Thread LoopThread ends.
    # Thread MainThread ends.
    
    
    def process_thread(student_name: str) -> None:
        """
        Processes a thread and put the student of the current thread to the
        ThreadLocal.
        :param student_name: str
        :return: None
        """
        thread_local.student = student_name  # 在ThreadLocal中绑定当前thread对应的student
        _greet_student()
    
    
    def _greet_student() -> None:
        """
        Greets the student of the current thread.
        :return:
        """
        student = thread_local.student  # 从ThreadLocal中获取当前thread关联的student
        th_name = current_thread().name
        print(f'Hello, {student} (in {th_name})')
    
    
    # Use threading.ThreadLocal to encapsulate data in each thread
    # ThreadLocal可以看做一个{thread: thread属性dict}的dict, 用于管理thread内部的数据
    # ThreadLocal封装了使用thread作为key检索对应的属性dict, 再使用属性名作为key检索属性值的细节
    thread_local = local()
    th_a = Thread(target=process_thread, args=(thread_local, 'Alice'),
                  name='Thread-A')
    th_b = Thread(target=process_thread, args=(thread_local, 'Bob'),
                  name='Thread-B')
    th_a.start()
    th_b.start()
    th_a.join()
    th_b.join()
    
    # Output:
    # Hello, Alice (in Thread-A)
    # Hello, Bob (in Thread-B)
    
    
    # 注意:
    # Python的thread虽然是真正的thread, 但解释器执行代码时, 有一个GIL锁 (Global Interpreter Lock)
    # 任何Python thread执行前, 必须先获得GIL, 然后, 每执行100条字节码, 解释器就自动释放GIL锁, 让别的thread有机会执行
    # (Python 2.x)
    # 所以, multi-threading在Python中只能交替进行
    # (即使100个thread跑在100核CPU上, 也只能用到1个核 => 不可能通过multi-threading实现parallelism)
    # 但由于每个process有各自独立的GIL, 可以通过multi-processing实现concurrency
    ```

  * Extending `threading.Thread` class, and override `run()` method

    ```python
    from threading import Thread
    
    import requests
    from bs4 import BeautifulSoup
    
    
    class MyThread(Thread):
        """
        My inherited thread class.
        """
        __slots__ = ['_page_num']
    
        _BASE_URL = 'https://movie.douban.com/top250?start={}&filter='
    
        def __init__(self, page_num: int):
            """
            Constructor with parameter.
            :param page_num: int
            """
            super().__init__()
            self._page_num = page_num
    
        def run(self):
            # Note that run() method is automatically called when start() method is
            # called
    
            url = self._BASE_URL.format(self._page_num * 25)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            title_tags = soup.find('ol', class_='grid_view').find_all('li')
            for title_tag in title_tags:
                title = title_tag.find('span', class_='title').text
                print(title)
    
    
    for page_num in range(10):
        th = MyThread(page_num)
        th.start()
    ```

* Using `concurrent.futures.ThreadPoolExecutor` to create a <u>pool</u> of threads

  ```python
  import concurrent.futures as cf
  
  import requests
  
  sites = [
      'http://europe.wsj.com/',
      'http://some-made-up-domain.com/',
      'http://www.bbc.co.uk/',
      'http://www.cnn.com/',
      'http://www.foxnews.com/',
  ]
  
  
  def site_size(url: str) -> int:
      """
      Returns the page size in bytes of the given URL.
      :param url: str
      :return: str
      """
      response = requests.get(url)
      return len(response.content)
  
  
  # Create a thread pool with 10 threads
  with cf.ThreadPoolExecutor(max_workers=10) as pool:
      # Submit tasks for execution
      future_to_url = {pool.submit(site_size, url): url for url in sites}
      # Wait until all the submitted tasks have been completed
      for future in cf.as_completed(future_to_url.keys()):
          url = future_to_url[future]
          try:
              # Get the execution result
              page_size = future.result()
          except Exception as e:
              print(f'{url} generated an exception: {e}')
          else:
              print(f'{url} page is {page_size} bytes.')
  
  # Output:
  # http://some-made-up-domain.com/ page is 301 bytes.
  # http://www.foxnews.com/ page is 216594 bytes.
  # http://www.cnn.com/ page is 1725827 bytes.
  # http://europe.wsj.com/ page is 979035 bytes.
  # http://www.bbc.co.uk/ page is 289252 bytes.
  ```

<br>

## Python Thread的wait和notify

### Condition (条件变量)

通常与一个锁关联, 需要在多个Condition中共享一个锁时, 可以传递一个Lock/RLock实例给constructor, 否则它将自己生成一个RLock实例

**相当于除了Lock带有的锁定池外,  Condition还自带一个等待池**

**构造方法:**

Condition(lock=None)

**实例方法:**

- `acquire(*args)` / `release()`

  调用关联的锁的相应方法

- `wait(timeout=None)`   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

  使当前thread进入Condition的等待池等待通知, 并释放锁

- `notify(n=1)`   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

  从Condition的等待池中随机挑选一个thread来通知, 收到通知的thread将自动调用acquire()来尝试获得锁定 (进入锁定池), 但当前thread不会释放锁

- `notify_all()`   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

  通知Condition的等待池中的全部thread, 收到通知的全部thread将自动调用acquire()来尝试获得锁定 (进入锁定吃), 但当前thread不会释放锁

<br>

#### 万恶的Python GIL (Global Interpreter Lock)

**在Python中, 某个thread想要执行, 必须先拿到GIL.**

*(我们可以把GIL看作是"通行证", 并且在一个Python process中, GIL只有一个. 拿不到通行证的thread, 就不允许进入CPU执行.)*

=> **由于GIL的存在, Python里一个process同一时间永远只能执行一个thread (即拿到GIL的thread才能执行)**; 而每次释放GIL, thread进行锁竞争、切换thread, 会消耗资源, 这就是为什么**Python即使是在多核CPU上, multi-threading的效率也并不高**

<br>

在Python multi-threading下, 每个thread的执行方式:

1. 获取process GIL

2. 执行代码直到sleep或者是Python虚拟机将其挂起

3. 释放process GIL

   - 遇到IO操作

     ​	=> **对于IO密集型程序, 可以在thread-A等待时, 自动切换到thread-B, 不浪费等待时间, 从而提升程序执行效率**

     ​	=> **Python multi-threading对IO密集型代码比较友好**

   - Python 2.x中, ticks计数达到100

     ​	=> 对于CPU计算密集型程序, 由于ticks会很快达到100, 然后进行释放GIL, thread进行锁竞争、切换thread, 导致资源消耗严重

   - Python 3.x中, 改为计时器达到某个阈值

     ​	=> 对于CPU计算密集型程序稍微友好了一些, 但依然没有解决根本问题

     => **Python multi-threading对CPU计算密集型代码不友好**

<br>

**结论: 多核下, 想做concurrent提升效率, 比较通用的方法是使用multi-processing, 能够有效提高执行效率**

*每个process有各自独立的GIL, 互不干扰, 这样就可以真正意义上的parallel执行.*

