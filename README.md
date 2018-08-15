This repo contains multi-threading in both Java and Python, as well as multi-processing in Python.

# Multi-threading

## Thread Safety

Thread-safe code must ensure that when multiple threads are accessing a shared object, no matter how these threads are scheduled or in what order they are executing, this object will always behave correctly without any external synchronization, and every thread will be able to see any changes happened on this object immediately.

## Race Condition

A program attempts to do some parallel operations at the same time, but requires that the operations are done in a specific order that is not guaranteed.

*They are difficult to detect because oftentimes, the ordering may be correct, making the system appear functional.*

**Away with Race Conditions:**

1. Ensure an explicit ordering of the operations

   All operations must be executed in the same order they are received.

2. Restrict access to a shared resource

   Only one operation can access the shared resource at the same time. During the period of access, no other operations can read or change its value.

## Thread的wait和notify

<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_wait.png?raw=true" width="400px">



<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_notify.png?raw=true" width="400px">

### 对于Java而言:

**In Java, every object has a unique internal lock.** When a method is declared as ``synchronized``, or a code snippet is enclosed by ``synchronized (this)`` block, that method or code snippet will be protected by an internal lock. When any thread wants to enter the method or the code snippet, it must first try to acquire the internal lock.

This ensures that onlt one method can be executed on the object at any given point. Other methods can invoke the method or enter the code snippet, howerver they have to wait until the running thread releases the lock by exiting from the protected area or call wait() on the lock.

**相当于每个Object自带一个锁 (被称为monitor), 即每个Object自带一个锁定池和等待池**

<br>

A thread becomes the owner of the object's monitor in one of the three ways:

* By executing a ``synchronized`` instance method of that object
* By executing the body of a ``synchronized`` statement that synchronizes on the object
* For objects of type Class, by executing a ``synchronized `` static method of that class

<br>

当前thread拥有某个object的monitor时, 可以选择obj.wait()来使自己进入等待阻塞, 同时释放obj的monitor

当obj的monitor之后的拥有者thread call了obj.notify(), 唤醒obj的等待池中的任意一个thread, 收到通知的thread将自动尝试获得obj的monitor (进入obj的锁定池), 但当前thread不会释放obj的monitor

若obj的monitor之后的拥有者thread call了obj.notifyAll(), 唤醒obj的等待池中的全部thread, 收到通知的全部thread将自动尝试获得obj的monitor (进入obj的锁定池), 但当前thread不会释放obj的monitor

*注意: 只有当某个thread重新获得了obj的monitor之后才会从obj.wait()中退出, 即obj.wait()涵盖了wait()和在obj的锁定池中成功获得锁定两部分*

<br>

注意:

A thread can also wake up without being notified, interrupted, or timing out, a so-called *spurious wakeup*. While this will rarely occur in practice, applications must guard against it by testing for the condition that should have caused the thread to be awakened, and continuing to wait if the condition is not satisfied. In other words, waits should always occur in loops, like this one:

```java
synchronized (obj) { // 执行synchronized block on obj, 获得obj的monitor
  while (<condition does not hold>) {
    obj.wait();
  }
  // Perform action appropriate to condition
}
```

<br>

注意:

A more common mistake is synchronizing on threads' own lock (``synchronized (this)``). Since each instance has its own internal block, by using thread's own lock, the code block is not protected by a global lock and every thread can access it at any time. Thus, this kind of synchronization will fail to work.

```java
// Bad example
public void uselessSync() {
  new Thread(new Runnable() {
    @Override
    public void run() {
      synchronized (this) { // Use the current thread's monitor as the lock, but not a global shared lock
        // Do something
      }
    }
  })
}
```

本质上: **Always synchronize on the same lock before accessing the shared object**

```java
// Good example
private Object lock = new Object();

public void sync() {
  new Thread(new Runnable() {
    @Override
    public void run() {
      synchronized (lock) { // Use a global shared lock
        // Do something
      }
    }
  })
}
```



<br>

### 对于Python而言:

#### Condition (条件变量)

通常与一个锁关联, 需要在多个Condition中共享一个锁时, 可以传递一个Lock/RLock实例给constructor, 否则它将自己生成一个RLock实例

**相当于除了Lock带有的锁定池外,  Condition还自带一个等待池**

**构造方法:**

Condition(lock=None)

**实例方法:**

* acquire(*args) / release()

  调用关联的锁的相应方法

* wait(timeout=None)   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

  使当前thread进入Condition的等待池等待通知, 并释放锁

* notify(n=1)   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

  从Condition的等待池中随机挑选一个thread来通知, 收到通知的thread将自动调用acquire()来尝试获得锁定 (进入锁定池), 但当前thread不会释放锁

* notify_all()   *(使用前当前thread必须已获得锁定, 否则将抛出异常)*

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

   * 遇到IO操作

     ​	=> **对于IO密集型程序, 可以在thread-A等待时, 自动切换到thread-B, 不浪费等待时间, 从而提升程序执行效率**

     ​	=> **Python multi-threading对IO密集型代码比较友好**

   * Python 2.x中, ticks计数达到100

     ​	=> 对于CPU计算密集型程序, 由于ticks会很快达到100, 然后进行释放GIL, thread进行锁竞争、切换thread, 导致资源消耗严重

   * Python 3.x中, 改为计时器达到某个阈值

     ​	=> 对于CPU计算密集型程序稍微友好了一些, 但依然没有解决根本问题

     => **Python multi-threading对CPU计算密集型代码不友好**

<br>

**结论: 多核下, 想做concurrent提升效率, 比较通用的方法是使用multi-processing, 能够有效提高执行效率**

*每个process有各自独立的GIL, 互不干扰, 这样就可以真正意义上的parallel执行.*

<br>

## Thread状态转换总结

<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_status.png?raw=true" width="450px">

## Thread-safety in Java Libraries

There are five levels thread-safety in Java library:

1. **Immutable**

   Immutable objects cannot be changed or modified, so we can safely share it among threads and do not need to do any synchronization.

2. **Unconditionally thread-safe**

   These objects are mutable, but have implemented sufficient "internal synchronization", which means that locking has already been designed and implemented by Java standard library developers, and we do not need to synchronize by ourselves manually. Thus, we can safely use them.

   e.g., AtomicInteger, Random, ConcurrentHashMap, ConcurrentHashSet, BlockingQueue, PriorityBlockingQueue...

   ```java
   ConcurrentHashSet<String> set = new ConcurrentHashSet<String>();
   
   public void add(String s) {
     set.add(s);
   }
   ```

3. **Conditionally thread-safe**

   These objects are mutable, but have implemented sufficient "internal synchronization" on most of the methods. However, some methods still need to explicitly perform external synchronization.

4. **Thread-unsafe**

   These objects are mutable and implemented with no internal synchronization. In order to use them safely, please explicitly synchronize ANY method call to these objects.

   e.g., StringBuilder, most of the Java Collections, such as ArrayList, LinkedList, HashMap, HashSet...

   ```java
   HashSet<String> set = new HashSet<String>();
   
   public synchronized void add(String s) {
     set.add(s);
   }
   ```

5. **Thread-hostile**

   These objects are not thread-safe even if you have already used external synchronization on ANY method call.

<br>

# License

This repo is distributed under the <a href="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/LICENSE">MIT license</a>.
