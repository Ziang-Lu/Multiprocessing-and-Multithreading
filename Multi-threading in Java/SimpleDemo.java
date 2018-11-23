/**
 * Self-defined class that implements Runnable interface.
 *
 * @author Ziang Lu
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
 * Self-defined class that extends Thread class.
 *
 * @author Ziang Lu
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
