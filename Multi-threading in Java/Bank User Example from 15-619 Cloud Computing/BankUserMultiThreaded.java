import java.util.PriorityQueue;

public class BankUserMultiThreaded {

    /**
     * Balance of the bank user.
     */
    private static int balance;
    /**
     * Min-heap for the deposit/withdraw operation timestamps.
     *
     * In order to ensure an explicit ordering of the deposit/withdraw
     * operations, i.e., all the operations must be executed in the order they
     * are received:
     * we create a min-heap of the timestamps of the deposit/withdraw operation.
     */
    private static final PriorityQueue<Long> operations = new PriorityQueue<>();

    /**
     * Adds the given amount to the balance.
     * No need to do authentication in deposit() method.
     * @param amt amount to deposit
     */
    public static void deposit(final int amt) {
        // Get the timestamp of the operation, and push it to the min-heap
        Long timestamp = getTime();
        operations.offer(timestamp);

        // Create a new thread for the deposit operation
        Thread th = new Thread(new Runnable() {
            @Override
            public void run() {
                // 尝试获得operations的monitor
                acquireLock(timestamp);
                // 当acquireLock()方法退出时, 当前线程已成功获得operations的monitor

                // No need to do authentication
                balance += amt;
                System.out.println(String.format("Deposit %d to funds. Not at %d", amt, balance));

                // 完成operation, 并释放operations的monitor
                releaseLock();
            }
        }, "Thread-Deposit");
        th.start();
    }

    /**
     * Private helper method to get the current timestamp.
     * @return current timestamp
     */
    private static Long getTime() {
        return System.nanoTime();
    }

    /**
     * Private helper method for the given operation timestamp's thread to
     * acquire operations's monitor.
     * @param timestamp given operation timestamp
     */
    private static void acquireLock(Long timestamp) {
        synchronized (operations) { // 尝试获得operations的monitor
            // 成功获得operations的monitor后

            // Check whether the operation to perform is the current operation
            while (timestamp != operations.peek()) {
                try {
                    operations.wait(); // 当前线程进入operations的等待池, 并释放operations的monitor
                } catch (InterruptedException ex) {
                    System.out.println(Thread.currentThread().getName() + " interrupted");
                }
            }
            // 此时, 当前的操作已经是下一步执行的操作, 且当前线程已再次获得operation的monitor
        }
    }

    /**
     * Private helper method for the current operation timestamp's thread to
     * release operation's monitor.
     */
    private static void releaseLock() {
        // Remove the timestamp of the operation just performed
        operations.poll();
        synchronized (operations) {
            operations.notifyAll(); // 通知operations的等待池中的全部线程来竞争operations的monitor
                                    // 根据第66行, 下一步操作的线程会成功获得operations的monitor而退出acquireLock()方法, 而对于
                                    // 不是下一步操作的线程, 该线程会重新进入operations的等待池
            // 注意这里不能用notify(), 因为一旦唤醒的不是下一步操作的线程, 根据第66行, 该线程会重新进入operations的等待池, 即全部线
            // 程都在operations的等待池中, 却没有一个再次唤醒另一个线程, 会导致deadlock
        }
    }

    /**
     * Private helper method to wait 50 milliseconds.
     */
    private static void wait_50ms() {
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            return;
        }
    }

    /**
     * Removes the given amount from the balance.
     * @param amt amount to withdraw
     */
    public static void withdraw(final int amt) {
        // Get the timestamp of the operation, and push it to the min-heap
        Long timestamp = getTime();
        operations.offer(timestamp);

        // Create a new thread responsible for the withdraw operation
        Thread th = new Thread(new Runnable() {
            @Override
            public void run() {
                // 尝试获得operations的monitor
                acquireLock(timestamp);
                // 当acquireLock()方法退出时, 当前线程已成功获得operations的monitor

                int holdings = balance;
                if (!authenticate()) { // authenticate() method always takes 500 milliseconds to run.
                    return;
                }
                if (holdings < amt) {
                    System.out.println(String.format(
                        "Overdraft Error: insufficient funds for this withdrawl. Balance = %d. Amt = %d", holdings, amt
                    ));
                    // 完成操作, 并释放operations的monitor
                    releaseLock();
                    return;
                }
                balance = holdings - amt;
                System.out.println(String.format("Withdraw %d from funds. Now at %d", amt, balance));

                // 完成操作, 并释放operations的monitor
                releaseLock();
            }
        }, "Thread-Withdraw");
        th.start();
    }

    /**
     * Private helper method to authenticate.
     * Due to poor optimization, this method always takes 500 milliseconds to
     * run.
     * @return whether the authentication succeeds
     */
    public static Boolean authenticate() {
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            System.out.println("ERROR: ABORT OPERATION, Authentication failed");
            return false;
        }
        return true;
    }

    public static void test_case0() {
        balance = 0;
        deposit(100);
        wait_50ms(); //
        deposit(200);
        wait_50ms(); //
        deposit(700);
        wait_50ms(); // To make sure the deposits are in the sequentially correct order
        if (balance == 1000) {
            System.out.println("Test passed!");
        } else {
            System.out.println("Test failed!");
        }
    }

    public static void test_case1() {
        balance = 0;
        deposit(100);
        deposit(200);
        deposit(700);
    }

    public static void test_case2() {
        balance = 0;
        deposit(1000);
        withdraw(1000);
        withdraw(1000);
        withdraw(1000);
        withdraw(1000);
        withdraw(1000);
    }

    public static void test_case3() {
        balance = 0;
        withdraw(1000);
        deposit(500);
        deposit(500);
        withdraw(500);
        withdraw(500);
        withdraw(1000);
    }

    public static void test_case4() {
        balance = 0;
        deposit(2000);
        withdraw(500);
        withdraw(1000);
        withdraw(1500);
        deposit(4000);
        withdraw(2000);
        withdraw(2500);
        withdraw(3000);
        deposit(5000);
        withdraw(3500);
        withdraw(4000);
    }

    public static void main(String[] args) {
        // Uncomment Tests Cases as you go
        // test_case0();
        // test_case1();
        // test_case2();
        // test_case3();
        test_case4();
    }

}
