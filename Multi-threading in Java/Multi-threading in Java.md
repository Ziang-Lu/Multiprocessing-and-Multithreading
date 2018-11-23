# Mult-threading in Java

## Java Thread的wait和notify

**In Java, every object has a unique internal lock.** When a method is declared as ``synchronized``, or a code snippet is enclosed by ``synchronized (this)`` block, that method or code snippet will be protected by an internal lock. When any thread wants to enter the method or the code snippet, it must first try to acquire the internal lock.

This ensures that onlt one method can be executed on the object at any given point. Other methods can invoke the method or enter the code snippet, howerver they have to wait until the running thread releases the lock by exiting from the protected area or call wait() on the lock.

**相当于每个Object自带一个锁 (被称为monitor), 即每个Object自带一个锁定池和等待池**

<br>

A thread becomes the owner of the object's monitor in one of the three ways:

- By executing a ``synchronized`` instance method of that object
- By executing the body of a ``synchronized`` statement that synchronizes on the object
- For objects of type Class, by executing a ``synchronized `` static method of that class

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

------

For better capabilities to <u>monitor the lock status</u>, check out Java `ReentrantLock`: https://docs.oracle.com/javase/10/docs/api/java/util/concurrent/locks/ReentrantLock.html

------

<br>

## Thread-safety in Java Libraries

There are five levels thread-safety in Java library:

1. **Immutable**

   Immutable objects cannot be changed or modified, so we can safely share it among threads and do not need to do any synchronization.

2. **Unconditionally thread-safe**

   These objects are mutable, but have implemented sufficient "internal synchronization", which means that locking has already been designed and implemented by Java standard library developers, and we do not need to synchronize by ourselves manually. Thus, we can safely use them.

   e.g., `AtomicInteger`, `Random`,` ConcurrentHashMap`, `ConcurrentHashSet`, `BlockingQueue`, `PriorityBlockingQueue`...

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

   e.g., `StringBuilder`, most of the Java `Collections`, such as `ArrayList`, `LinkedList`, `HashMap`, `HashSet`...

   ```java
   HashSet<String> set = new HashSet<String>();
   
   public synchronized void add(String s) {
     set.add(s);
   }
   ```

5. **Thread-hostile**

   These objects are not thread-safe even if you have already used external synchronization on ANY method call.

