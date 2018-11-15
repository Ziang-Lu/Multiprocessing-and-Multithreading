import java.util.concurrent.locks.ReentrantLock;

/**
 * ReentrantLock simple demo.
 *
 * @author Ziang Lu
 */
public class ReentrantLockDemo extends Thread {

    /**
     * Shared reentrant lock.
     */
    private static ReentrantLock lock = new ReentrantLock();
    /**
     * Counter used for demo.
     */
    private static int i = 0;

    /**
     * Constructor with parameter.
     * @param threadName thread name
     */
    private ReentrantLockDemo(String threadName) {
        super(threadName);
    }

    @Override
    public void run() {
        for (int j = 0; j < 100; ++j) {
            lock.lock();
            lock.lock();
            try {
                System.out.println("Current thread holding the lock? " + lock.isHeldByCurrentThread()); // true
                System.out.println("Current thread hold count: " + lock.getHoldCount()); // 2
                System.out.println(getName() + " " + i);
                ++i;
            } finally {
                lock.unlock();
                lock.unlock();
            }
        }
    }

    /**
     * Main driver.
     * @param args arguments from command line
     */
    public static void main(String[] args) {
        ReentrantLockDemo demo1 = new ReentrantLockDemo("Thread-1");
        ReentrantLockDemo demo2 = new ReentrantLockDemo("Thread-2");

        demo1.start();
        demo2.start();

        try {
            demo1.join();
            demo2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println(i);
    }

}
