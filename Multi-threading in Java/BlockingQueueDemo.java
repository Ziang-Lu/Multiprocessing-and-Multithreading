import java.util.Random;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

/**
 * Producer class.
 * Writes data to an atomic message queue
 */
class Producer implements Runnable {
    /**
     * Random number generator to use.
     */
    private final Random random;
    /**
     * Atomic message queue used by this producer.
     */
    private final BlockingQueue<String> queue;

    /**
     * Constructor with parameter.
     * @param queue atomic message queue to use
     */
    Producer(BlockingQueue<String> queue) {
        random = new Random();
        this.queue = queue;
    }

    @Override
    public void run() {
        try {
            // Produce messages
            for (int i = 0; i < 5; ++i) {
                // Simulate the producing process by sleeping for 1~3 seconds
                Thread.sleep((random.nextInt(2)  + 1) * 1000);
                String msg = String.format("Message-%d", i);
                queue.put(msg);
                System.out.println("Producer put " + msg + " into the queue");
            }
            // Put a special value indicating that the message queue should shut down
            queue.put("exit");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

/**
 * Consumer class.
 * Reads data from an atomic message queue
 */
class Consumer implements Runnable {
    /**
     * Random number generator to use.
     */
    private final Random random;
    /**
     * Atomic queue used by this consumer.
     */
    private final BlockingQueue<String> queue;

    /**
     * Constructor with parameter.
     * @param queue atomic message queue to use
     */
    Consumer(BlockingQueue<String> queue) {
        random = new Random();
        this.queue = queue;
    }

    @Override
    public void run() {
        try {
            String msg = queue.take();
            // Check for the special value indicating that the message queue should shut down
            while (!msg.equals("exit")) {
                System.out.println("Consumer got " + msg + " from the queue");
                // Simulate the consuming process by sleeping for 1~5 seconds
                Thread.sleep((random.nextInt(4)  + 1) * 1000);
                msg = queue.take();
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

/**
 * Simple demo for using BlockingQueue as an atomic message queue.
 *
 * @author Ziang Lu
 */
public class BlockingQueueDemo {

    /**
     * Main driver.
     * @param args arguments from command line
     */
    public static void main(String[] args) {
        BlockingQueue<String> queue = new ArrayBlockingQueue<>(3);
        new Thread(new Producer(queue)).start();
        new Thread(new Consumer(queue)).start();

        /*
         * Output:
         * Producer put Message-0 into the queue
         * Consumer got Message-0 from the queue
         * Producer put Message-1 into the queue
         * Consumer got Message-1 from the queue
         * Producer put Message-2 into the queue
         * Consumer got Message-2 from the queue
         * Producer put Message-3 into the queue
         * Producer put Message-4 into the queue
         * Consumer got Message-3 from the queue
         * Consumer got Message-4 from the queue
         */
    }

}
