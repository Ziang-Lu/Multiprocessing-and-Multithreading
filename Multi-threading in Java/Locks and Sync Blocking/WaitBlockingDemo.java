/**
 * Self-defined queue to synchronize on.
 */
class MyQueue {
    /**
     * Underlying number in the queue.
     */
    private int n;
    /**
     * Whether the number is set by put() method.
     */
    boolean numIsSet = false;

    /**
     * Accessor of n.
     * @return n
     */
    int get() {
        System.out.println("Got " + n + " from queue");
        return n;
    }

    /**
     * Mutator of n
     * @param n n
     */
    void put(int n) {
        System.out.println("Put " + n + " into the queue");
        this.n = n;
    }
}

/**
 * Self-defined Producer class that implements Runnable interface.
 * Writes data to a synchronized queue
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
        int i = 0;
        while (i <= 5) {
            synchronized (queue) { // 1. 成功获得queue的monitor   [等待池: 空, 锁定池: 空, 已锁定: P]
                while (queue.numIsSet) {
                    try {
                        System.out.println("Producer waiting...");
                        queue.wait(); // 3. 当前线程进入queue的等待池, 并释放queue的monitor   [等待池: P, 锁定池: C, 已锁定: 空]
                                      // 4. 接到通知, 自动尝试获得queue的monitor(进入锁定池)   [等待池: 空, 锁定池: P, 已锁定: C]
                                      // 5. 由于C释放了queue的monitor, 成功获得queue的monitor   [等待池: C, 锁定池: 空, 已锁定: P]
                                      // 7 -> 3
                        System.out.println("Producer got queue's monitor");
                    } catch (InterruptedException e) {
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
        while (true) {
            synchronized (queue) { // 1. 尝试获得queue的monitor, 同步阻塞在queue的锁定池中   [等待池: 空, 锁定池: C, 已锁定: P]
                                   // 3. 由于P释放了queue的monitor, 成功获得queue的monitor   [等待池: P, 锁定池: 空, 已锁定: C]
                while (!queue.numIsSet) {
                    try {
                        System.out.println("Consumer waiting...");
                        queue.wait(); // 5. 当前线程进入queue的等待池, 并释放queue的monitor   [等待池: C, 锁定池: P, 已锁定: 空]
                                      // 6. 接到通知, 当前线程自动尝试获得queue的monitor(进入queue的锁定池)   [等待池: 空, 锁定池: C, 已锁定: P]
                                      // 7 -> 3
                        System.out.println("Consumer got queue's monitor");
                    } catch (InterruptedException e) {
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
        Thread producer = new Thread(new Producer(queue), "Thread-Producer");
        Thread consumer = new Thread(new Consumer(queue), "Thread-Consumer");
        producer.start();
        consumer.start();
        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            System.out.println(Thread.currentThread().getName() + " interrupted");
        }

        /*
         * Output:
         * Put: 1 into the queue
         * Producer waiting...
         * Got: 1 from queue
         * Consumer waiting...
         * Producer got queue's monitor
         * Put: 2 into the queue
         * Producer waiting...
         * Consumer got queue's monitor
         * Got: 2 from queue
         * Consumer waiting...
         * Producer got queue's monitor
         * Put: 3 into the queue
         * Producer waiting...
         * Consumer got queue's monitor
         * Got: 3 from queue
         * Consumer waiting...
         * Producer got queue's monitor
         * Put: 4 into the queue
         * Producer waiting...
         * Consumer got queue's monitor
         * Got: 4 from the queue
         * Consumer waiting...
         * Producer got queue's monitor
         * Put: 5 into the queue
         * Consumer got queue's monitor
         * Got: 5 from the queue
         * Consumer waiting...
         */
    }

}
