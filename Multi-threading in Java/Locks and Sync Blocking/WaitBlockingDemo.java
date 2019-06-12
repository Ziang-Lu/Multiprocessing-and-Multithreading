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
            synchronized (queue) {
                while (queue.numIsSet) {
                    try {
                        System.out.println("Producer waiting...");
                        queue.wait();
                        System.out.println("Producer got queue's monitor");
                    } catch (InterruptedException e) {
                        System.out.println(Thread.currentThread().getName() + " interrupted");
                    }
                }
                queue.put(i);
                queue.numIsSet = true;
                queue.notify();
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
            synchronized (queue) {
                while (!queue.numIsSet) {
                    try {
                        System.out.println("Consumer waiting...");
                        queue.wait();
                        System.out.println("Consumer got queue's monitor");
                    } catch (InterruptedException e) {
                        System.out.println(Thread.currentThread().getName() + " interrupted");
                    }
                }
                queue.get();
                queue.numIsSet = false;
                queue.notify();
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
