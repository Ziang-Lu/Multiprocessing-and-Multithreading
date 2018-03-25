import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;

/**
 * Self-defined class that implements Runnable interface.
 */
class MyRunnable implements Runnable {
    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        System.out.println("Running thread " + threadName + "...");
        try {
            for (int i = 0; i < 3; ++i) {
                System.out.println("Thread " + threadName + " >>> " + i);
                Thread.sleep((long) (500 + Math.random() * 500));
            }
        } catch (InterruptedException ex) {
            System.out.println("Thread " + threadName + " interrupted");
        }
        System.out.println("Thread " + threadName + " exited");
    }
}

/**
 * Self-defined class that extends Thread class.
 */
class MyThread extends Thread {
    /**
     * Constructor with parameter.
     * @param name thread name
     */
    MyThread(String name) {
        super(name);
    }

    @Override
    public void run() {
        String threadName = Thread.currentThread().getName();
        System.out.println("Running thread " + threadName + "...");
        try {
            for (int i = 0; i < 3; ++i) {
                System.out.println("Thread " + threadName + " >>> " + i);
                Thread.sleep((long) (500 + Math.random() * 500));
            }
        } catch (InterruptedException ex) {
            System.out.println("Thread " + threadName + " interrupted");
        }
        System.out.println("Thread " + threadName + " exited");
    }
}

/**
 * Self-defined class that implements Callable interface.
 */
class MyCallable implements Callable<Integer> {
    @Override
    public Integer call() throws Exception {
        int i = 0;
        for (; i < 5; ++i) {
            System.out.println(Thread.currentThread().getName() + " >>> " + i);
        }
        return i;
    }
}

public class BasicImplementations {

    /**
     * Main driver.
     * @param args arguments from command line
     */
    public static void main(String[] args) {
        // Create threads by creating class that implements Runnable interface
        Thread th1 = new Thread(new MyRunnable(), "Thread-1"), th2 = new Thread(new MyRunnable(), "Thread-2");
        try {
            th1.start();
            th2.start();
            th1.join();
            th2.join();
        } catch (InterruptedException ex) {
            System.out.println("Thread " + Thread.currentThread().getName() + " interrupted");
        }
        System.out.println();

        /*
         * Output:
         * Running thread Thread-1...
         * Running thread Thread-2...
         * Thread Thread-2 >>> 0
         * Thread Thread-1 >>> 0
         * Thread Thread-1 >>> 1
         * Thread Thread-2 >>> 1
         * Thread Thread-1 >>> 2
         * Thread Thread-2 >>> 2
         * Thread Thread-1 exited
         * Thread Thread-2 exited
         */

        // Create threads by creating class that extends Thread class
        Thread th3 = new MyThread("Thread-3"), th4 = new MyThread("Thread-4");
        try {
            th3.start();
            th4.start();
            th3.join();
            th4.join();
        } catch (InterruptedException ex) {
            System.out.println("Thread " + Thread.currentThread().getName() + " interrupted");
        }
        System.out.println();

        /*
         * Output:
         * Running thread Thread-3...
         * Running thread Thread-4...
         * Thread Thread-3 >>> 0
         * Thread Thread-4 >>> 0
         * Thread Thread-3 >>> 1
         * Thread Thread-4 >>> 1
         * Thread Thread-3 >>> 2
         * Thread Thread-4 >>> 2
         * Thread Thread-3 exited
         * Thread Thread-4 exited
         */

        // Create threads by creating class that implements Callable interface, and encapsulate it by FutureTask
        FutureTask<Integer> ft = new FutureTask<>(new MyCallable());
        for (int i = 0; i < 10; ++i) {
            System.out.println(Thread.currentThread().getName() + " >>> " + i);
            if (i == 5) {
                Thread th = new Thread(ft, "ThreadWithReturnValue"); // Use FutureTask as the target of a thread
                th.start();
            }
        }
        try {
            System.out.println("Subthread return value: " + ft.get()); // Call FutureTask.get() method to get the
                                                                       // return value of the thread
        } catch (InterruptedException ex) {
            ex.printStackTrace();
        } catch (ExecutionException ex) {
            ex.printStackTrace();
        }

        /*
         * Output:
         * main >>> 0
         * main >>> 1
         * main >>> 2
         * main >>> 3
         * main >>> 4
         * main >>> 5
         * main >>> 6
         * main >>> 7
         * main >>> 8
         * main >>> 9
         * ThreadWithReturnValue >>> 0
         * ThreadWithReturnValue >>> 1
         * ThreadWithReturnValue >>> 2
         * ThreadWithReturnValue >>> 3
         * ThreadWithReturnValue >>> 4
         * Subthread return value: 5
         */
    }

}
