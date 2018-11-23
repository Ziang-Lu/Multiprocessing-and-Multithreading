# Multi-threading in Python

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

