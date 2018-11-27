# Mult-threading in Java

## Basic Implementations

* Implementing `Runnable` interface, and therefore implement `run()` method

  ```java
  /**
   * Self-defined class that implements Runnable interface.
   */
  class DisplayMessage implements Runnable {
      /**
       * Message to display.
       */
      private final String msg;
  
      /**
       * Constructor with parameter.
       * @param msg message to display
       */
      DisplayMessage(String msg) {
          this.msg = msg;
      }
  
      @Override
      public void run() {
          try {
              for (int i = 0; i < 3; ++i) {
                  System.out.println(msg);
                  Thread.sleep((long) (500 + Math.random() * 500));
              }
          } catch (InterruptedException ex) {
              System.out.println(Thread.currentThread().getName() + " interrupted");
          }
      }
  }
  
  /**
   * Simple demo for multi-threading with implementing Runnable interface.
   *
   * @author Ziang Lu
   */
  public class SimpleDemo {
  
      /**
       * Main driver.
       * @param args arguments from command line
       */
      public static void main(String[] args) {
          Thread helloThread = new Thread(new DisplayMessage("hello"), "Thread-Hello");
          System.out.println("Starting hello thread...");
          helloThread.start();
  
          Thread byeThread = new Thread(new DisplayMessage("bye"), "Thread-Bye");
          System.out.println("Starting bye thread...");
          byeThread.start();
  
          try {
              helloThread.join();
              byeThread.join();
          } catch (InterruptedException ex) {
              System.out.println(Thread.currentThread().getName() + " interrupted");
          }
          System.out.println();
  
          /*
           * Output:
           * Starting hello thread...
           * Starting bye thread...
           * hello
           * bye
           * hello
           * bye
           * hello
           * bye
           */
      }
  
  }
  ```

* Extending `Thread` class, and override `run()` method

  ```java
  /**
   * Self-defined class that extends Thread class.
   */
  class GuessANumber extends Thread {
      /**
       * Number to guess.
       */
      private final int num;
  
      /**
       * Constructor with parameter.
       * @param num number to guess
       */
      GuessANumber(int num) {
          this.num = num;
      }
  
      @Override
      public void run() {
          String threadName = Thread.currentThread().getName();
          int counter = 0;
          int guess = 0;
          do {
              guess = (int) (Math.random() * 10 + 1);
              System.out.println(threadName + " guesses " + guess);
              ++counter;
          } while (guess != num);
          System.out.println("Correct! " + threadName + " uses " + counter + " guesses.");
      }
  }
  
  /**
   * Simple demo for multi-threading with extending Thread class.
   *
   * @author Ziang Lu
   */
  public class SimpleDemo {
  
      /**
       * Main driver.
       * @param args arguments from command line
       */
      public static void main(String[] args) {
          Thread guessThread = new GuessANumber(7);
          guessThread.setName("Thread-Guess");
          System.out.println("Starting guess thread...");
          guessThread.start();
          try {
              guessThread.join();
          } catch (InterruptedException ex) {
              System.out.println(Thread.currentThread().getName() + " interrupted");
          }
  
          /*
           * Output:
           * Starting guess thread...
           * Thread-Guess guesses 9
           * Thread-Guess guesses 8
           * Thread-Guess guesses 1
           * Thread-Guess guesses 7
           * Correct! Thread-Guess uses 4 guesses.
           */
      }
  
  }
  ```

* Use `ExecutorService` class to create a <u>pool</u> of threads

  ```java
  import java.util.Random;
  import java.util.concurrent.ExecutorService;
  import java.util.concurrent.Executors;
  import java.util.concurrent.TimeUnit;
  
  /**
   * Self-defined class that implements Runnable interface.
   */
  class Task implements Runnable {
      /**
       * Task ID.
       */
      private int id;
      /**
       * Random number generator to use.
       */
      private Random random;
  
      /**
       * Constructor with parameter.
       * @param id task ID
       */
      Task(int id) {
          this.id = id;
          random = new Random();
      }
  
      @Override
      public void run() {
          System.out.println("Starting task-" + id);
          // To simulate the task execution, sleep a random period between 1~5 seconds
          try {
              Thread.sleep((random.nextInt(4) + 1) * 1000);
          } catch (InterruptedException e) {
              e.printStackTrace();
          }
          System.out.println("Completed task-" + id);
      }
  }
  
  /**
   * Simple demo for creating and using a thread pool.
   *
   * @author Ziang Lu
   */
  public class ThreadPoolDemo {
  
      /**
       * Main driver.
       * @param args arguments from command line
       */
      public static void main(String[] args) {
          // Create a thread pool with 3 threads
          ExecutorService pool = Executors.newFixedThreadPool(3);
          // Submit tasks for execution
          for (int i = 0; i < 5; ++i) {
              pool.submit(new Task(i));
          }
          // We need to call shutdown() to indicate to the executor service (thread pool) that no more tasks are allowed
          // to be submitted.
          // If we don't call shutdown(), the program will never end, since the executor service (thread pool) keeps
          // waiting for more tasks to be submitted.
          pool.shutdown();
          // After calling shutdown(), no more tasks are allowed to be submitted; when all the submitted tasks finished
          // execution, this executor service (thread pool) is terminated.
          System.out.println("All tasks submitted and the executor service (thread pool) is shut down.");
  
          // Check: After calling shutdown(), submitting a new task throws a RejectedExecutionException
  //        pool.submit(new Task(5));
  
          // Wait up to 60 seconds for all the submitted tasks to finish execution
          System.out.println("Waiting for all tasks to finish execution...");
          try {
              pool.awaitTermination(60, TimeUnit.SECONDS); // Block until all the submitted tasks finish execution
          } catch (InterruptedException e) {
              e.printStackTrace();
              pool.shutdownNow();
              // This will force the executor service (thread pool) to shut down and terminate, by attempting to stop the
              // executing tasks, and prevent waiting tasks from starting.
          }
          // Upon termination, the executor service has no tasks actively executing, no tasks currently awaiting
          // execution, and no new tasks are allowed to be submitted
          System.out.println("All tasks completed.");
  
          /*
           * Output:
           * All tasks submitted and the executor service (thread pool) is shut down.
           * Waiting for all tasks to finish execution...
           * Starting task-2
           * Starting task-1
           * Starting task-0
           * Completed task-2
           * Completed task-0
           * Starting task-4
           * Starting task-3
           * Completed task-1
           * Completed task-3
           * Completed task-4
           * All tasks completed.
           */
      }
  
  }
  ```

<br>

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

<br>

## Thread-safety in Java Libraries

There are five levels thread-safety in Java library:

1. **Immutable**

   Immutable objects cannot be changed or modified, so we can safely share it among threads and do not need to do any synchronization.

2. **Unconditionally thread-safe**

   These objects are mutable, but have implemented sufficient "internal synchronization", which means that locking has already been designed and implemented by Java standard library developers, and we do not need to synchronize by ourselves manually. Thus, we can safely use them.

   e.g., `AtomicInteger`, `Random`, ` ConcurrentHashMap`, `ConcurrentHashSet`, `BlockingQueue`, `PriorityBlockingQueue`...

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

