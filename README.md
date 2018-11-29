# Multi-threading

## Thread Safety

Thread-safe code must ensure that when multiple threads are accessing a shared object, no matter how these threads are scheduled or in what order they are executing, this object will always behave correctly without any external synchronization, and every thread will be able to see any changes happened on this object immediately.

<br>

## Race Condition

A program attempts to do some parallel operations at the same time, but requires that the operations are done in a specific order that is not guaranteed.

*(They are difficult to detect because oftentimes, the ordering may be correct, making the system appear functional.)*

**Whenever there is read from/write to shared global variables, there could be race condition.**

=> Check out `Multi-processsing and Multi-threading in Python Examples/Multi-threading/race_condition_demo/race_condition.py`

### Away with Race Conditions: (-> Thread-Safe)

1. Ensure an explicit ordering of the operations (on the shared resources)

   All operations (on the shared resources) must be executed in the same order they are received.

   *=> To ensure this, we simply put the operations (on one shared resource) in a single thread.*

2. Restrict access to the shared resource

   Only one operation can access the shared resource at the same time. During the period of access, no other operations can read or change its value.

#### 1. Solution with Immutable Objects

Check out this design pattern: <a href="https://github.com/Ziang-Lu/Design-Patterns/blob/master/5-Concurrency%20Patterns/2-Immutable-Object%20Pattern.md">Immutable Object Pattern</a> for more details

<u>Since a class must have a lot of restrictions to be immutable, this solution is not very feasible in many practical cases.</u>

#### 2. Solution with Atomic Operations & Classes ***

**Atomic operations are performed in a single unit of task, without interference from other operations.**

e.g., Java `AtomicInteger`, `Random`, `ConcurrentHashMap`, `ConcurrentHashSet`, and the following (atomic) blocking queue interface and implementations

***

Solution with **(Atomic) Message Queue** ***

1. (对应于上面的1) Each shared resource shall be accessed in exactly its own thread.
2. (对应于上面的2) All communications with that thread shall be done using an atomic message queue
   * Java: `BlockingQueue` interface, with `ArrayBlockingQueue`, `LinkedBlockingQueue` and `PriorityBlockingQueue` impelementations
   * Python: `queue.Queue` and `queue.PriorityQueue` classes

***

#### 3. Solution with Locks ***

Note that <u>many solutions above</u>, like Atomic Operations & Classes and (Atomic) Message Queue, <u>have built-in locks in their implementations</u>, so  <u>using locks explicitly is considered a low-level synchronization operation</u> and should be avoided

<br>

## Thread的wait和notify

<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_wait.png?raw=true" width="400px">



<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_notify.png?raw=true" width="400px">

<br>

## Thread状态转换总结

<img src="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/thread_status.png?raw=true" width="450px">

<br>

# License

This repo is distributed under the <a href="https://github.com/Ziang-Lu/Multiprocessing-and-Multithreading/blob/master/LICENSE">MIT license</a>.
