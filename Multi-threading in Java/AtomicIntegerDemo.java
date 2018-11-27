import java.util.concurrent.atomic.AtomicInteger;

class Processing implements Runnable {
//    private int processedCount = 0;
    private AtomicInteger processedCount = new AtomicInteger();

    int getProcessedCount() {
//        return processedCount;
        return processedCount.get();
    }

    @Override
    public void run() {
        for (int i = 1; i < 5; ++i) {
            processSomeTask(i);
            System.out.println(Thread.currentThread().getName() + " finished processing task-" + i);

            // Wrong implementation:
//            ++processedCount;
            // Normal integer increment is NOT atomic, resulting in race condition and thus wrong final result.

            // Correct implementation: Use AtomicInteger
            processedCount.incrementAndGet();
            // AtomicInteger increment is atomic
        }
    }

    private void processSomeTask(int i) {
        try {
            Thread.sleep(i * 1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

/**
 * Simple demo for using AtomicInteger for atomic operations.
 *
 * @author Ziang Lu
 */
public class AtomicIntegerDemo {

    /**
     * Main driver.
     * @param args arguments from command line
     */
    public static void main(String[] args) {
        Processing sharedRunnable = new Processing();
        Thread th1 = new Thread(sharedRunnable, "Thread-1"), th2 = new Thread(sharedRunnable, "Thread-2");
        th1.start();
        th2.start();
        try {
            th1.join();
            th2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("Total processed count: " + sharedRunnable.getProcessedCount());

        /*
         * Output:
         * Thread-1 finished processing task-1
         * Thread-2 finished processing task-1
         * Thread-2 finished processing task-2
         * Thread-1 finished processing task-2
         * Thread-1 finished processing task-3
         * Thread-2 finished processing task-3
         * Thread-1 finished processing task-4
         * Thread-2 finished processing task-4
         * Total processed count: 8
         */
    }

}
