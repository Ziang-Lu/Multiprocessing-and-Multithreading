/**
 * Self-defined queue to synchronize on.
 *
 * @author Ziang Lu
 */
class MyQueue {
    /**
     * Underlying number in the queue.
     */
    private int n;
    /**
     * Whether the number is set by put() method.
     */
    boolean numIsSet;

    /**
     * Accessor of n.
     * @return n
     */
    int get() {
        System.out.println("Got: " + n);
        return n;
    }

    /**
     * Mutator of n
     * @param n n
     */
    void put(int n) {
        System.out.println("Put: " + n);
        this.n = n;
    }
}

/**
 * Self-defined Producer class that implements Runnable interface.
 * Writes data to a synchronized queue
 *
 * @author Ziang Lu
 */
class Producer implements Runnable {
    /**
     * Queue to write data to.
     */
    private final MyQueue queue;

    /**
     * Constructor with parameter.
     * @param queue queue to write data to
     */
    Producer(MyQueue queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
//        // Wrong implementation
//        int i = 1;
//        while (i <= 5) {
//            queue.put(i);
//            ++i;
//        }

        // Correct implementation
        int i = 0;
        while (i <= 5) {
            synchronized (queue) { // 1. 成功获得queue的monitor   [等待池: 空, 锁定池: 空, 已锁定: P]
                while (queue.numIsSet) {
                    try {
                        System.out.println("Waiting in producer...");
                        queue.wait(); // 3. 当前线程进入queue的等待池, 并释放queue的monitor   [等待池: P, 锁定池: C, 已锁定]
                                      // 4. 接到通知, 自动尝试获得queue的monitor(进入锁定池)   [等待池: 空, 锁定池: P, 已锁定: C]
                                      // 5. 由于C释放了queue的monitor, 成功获得queue的monitor   [等待池: C, 锁定池: 空, 已锁定: P]
                                      // 7 -> 3
                        System.out.println("Producer got queue's monitor");
                    } catch (InterruptedException ex) {
                        System.out.println(Thread.currentThread().getName() + " interrupted");
                    }
                }
                queue.put(i);
                queue.numIsSet = true;
                queue.notify(); // 2. 由于queue的等待池为空, 并没有通知任何线程, 且不会释放queue的monitor   [等待池: 空, 锁定池: C, 已锁定: P]
                                // 6. 通知C, C自动尝试获得queue的monitor(进入queue的锁定池), 但当前线程不会释放queue的monitor   [等待池: 空, 锁定池: C, 已锁定: P]
                ++i;
            }
        }
    }
}

/**
 * Self-defined Consumer class that implements Runnable interface.
 * Reads data from a synchronized queue
 *
 * @author Ziang Lu
 */
class Consumer implements Runnable {
    /**
     * Queue to read data from.
     */
    private final MyQueue queue;

    /**
     * Constructor with parameter.
     * @param queue queue to read data from
     */
    Consumer(MyQueue queue) {
        this.queue = queue;
    }

    @Override
    public void run() {
//        // Wrong implementation
//        while (true) {
//            queue.get();
//        }

        // Correct implementation
        while (true) {
            synchronized (queue) { // 1. 尝试获得queue的monitor, 同步阻塞在queue的锁定池中   [等待池: 空, 锁定池: C, 已锁定: P]
                                   // 3. 由于P释放了queue的monitor, 成功获得queue的monitor   [等待池: P, 锁定池: 空, 已锁定: C]
                while (!queue.numIsSet) {
                    try {
                        System.out.println("Waiting in consumer...");
                        queue.wait(); // 5. 当前线程进入queue的等待池, 并释放queue的monitor   [等待池: C, 锁定池: P, 已锁定: 空]
                                      // 6. 接到通知, 当前线程自动尝试获得queue的monitor(进入queue的锁定池)   [等待池: 空, 锁定池: C, 已锁定: P]
                                      // 7 -> 3
                        System.out.println("Consumer got queue's monitor");
                    } catch (InterruptedException ex) {
                        System.out.println(Thread.currentThread().getName() + " interrupted");
                    }
                }
                queue.get();
                queue.numIsSet = false;
                queue.notify(); // 4. 通知P, P自动尝试获得queue的monitor(进入queue的锁定池), 但当前线程不会释放queue的monitor   [等待池: 空, 锁定池: P, 已锁定: C]
            }
        }
    }
}

public class WaitBlockingDemo {

    /**
     * Main driver.
     * @param args arguments from command line
     */
    public static void main(String[] args) {
        MyQueue queue = new MyQueue();
        Thread producerThread = new Thread(new Producer(queue), "Thread-Producer");
        Thread consumerThread = new Thread(new Consumer(queue), "Thread-Consumer");
        producerThread.start();
        consumerThread.start();
        try {
            producerThread.join();
            consumerThread.join();
        } catch (InterruptedException ex) {
            System.out.println(Thread.currentThread().getName() + " interrupted");
        }
    }

}

/*
 * Output:
 * Put: 1
 * Waiting in producer...
 * Got: 1
 * Waiting in consumer...
 * Producer got queue's monitor
 * Put: 2
 * Waiting in producer...
 * Consumer got queue's monitor
 * Got: 2
 * Waiting in consumer...
 * Producer got queue's monitor
 * Put: 3
 * Waiting in producer...
 * Consumer got queue's monitor
 * Got: 3
 * Waiting in consumer...
 * Producer got queue's monitor
 * Put: 4
 * Waiting in producer...
 * Consumer got queue's monitor
 * Got: 4
 * Waiting in consumer...
 * Producer got queue's monitor
 * Put: 5
 * Consumer got queue's monitor
 * Got: 5
 * Waiting in consumer...
 */
