

import static org.junit.Assert.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTimeoutPreemptively;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.security.Permission;
import java.time.Duration;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;

class ExampleHwTestCases {


	/** 
	 * Output stream where we will print test outcomes.
	 * We don't use System.out and System.err to avoid any print statements in student's code.
	 */
	private static PrintStream originalOut = System.out;
	private static ByteArrayOutputStream testReadableOutputStream = new ByteArrayOutputStream();
	private static PrintStream testOut = new PrintStream(testReadableOutputStream);
	
	private static ExampleHw hw;
	private final static double TOTAL_POINTS = 100;
	private final static double NUMBER_OF_TEST_CASES = 4;
	private final static double POINTS_PER_TEST = TOTAL_POINTS/NUMBER_OF_TEST_CASES;
	
	/**
	 * Having tests time out is a good idea to avoid any infinite loops or
	 * infinite recursion in student's code, and to test for performance requirements.
	 */
	private final static Duration TEST_TIMEOUT = Duration.ofSeconds(2000);
	
	static double pointsEarned;
	static double grade = 0;

	@AfterAll
	static void printGrade() {
		testOut.println(String.format("You scored a %.2f out of %.2f", grade, TOTAL_POINTS));
		System.out.println(testReadableOutputStream.toString());
		System.setOut(testOut);
	}

	@BeforeEach
	void setUp(TestInfo testInfo) throws Exception {
		/*
		 *  This SecurityManger prevents program from exiting prematurely due to a
		 *	System.exit() call in student's code. Without this, tests would stop
		 *	running after a System.exit(). Removing it is NOT recommended.
		 */
		System.setSecurityManager(new NoExitSecurityManager());
		
		/*
		 *  Points earned in this test. Set to 0 before each test and increase it
		 *	accordingly in each of the test cases below.
		 */
		pointsEarned = 0;
		
		testOut.println("Test Case \"" + testInfo.getDisplayName() + "\": ");
		try {
			Integer[] arr = new Integer[] { 3, 5, 1, 9, 7 };
			hw = new ExampleHw(arr);
		} catch(Exception e) {
			/*
			 * Instantiating or initializing student's code ran into an error
			 * before we could test anything. Print a test failure message and
			 * re-throw the exception.
			 * 
			 * We re-throw the exception to let JUnit know that the test failed.
			 * Otherwise, since the exception was caught, JUnit may not mark
			 * the test as unsuccessful.
			 */

			String failMsg = "\t(" + e.getClass().getName() + ") " + e.getMessage();
			testOut.println(failMsg);
			
			throw e;
		}
	}

	@AfterEach
	void tearDown() throws Exception {
		// Removing NoExitSecurityManager. No need to modify.
		System.setSecurityManager(null);
		
		// Add some spacing between test case outputs
		testOut.println();
	}

	@Test
	@DisplayName("isSorted returns true when sorted")
	public void testIsSorted(TestInfo testInfo) {
		String failMsg = "Returned false when expected true.";
		assertSafely(() -> {
			hw = new ExampleHw(new Integer[] { 1, 3, 5, 7, 9 });
			assertTrue(hw.isSorted());
			pointsEarned = POINTS_PER_TEST;
		}, failMsg);
	}
	
	@Test
	@DisplayName("isSorted returns false when unsorted")
	public void testIsNotSorted(TestInfo testInfo) {
		String failMsg = "Returned true when expected false.";
		assertSafely(() -> {
			assertFalse(hw.isSorted());
			pointsEarned = POINTS_PER_TEST;
		}, failMsg);
	}
	
	@Test
	@DisplayName("getSortedArray returns the sorted array")
	public void testGetSortedArray(TestInfo testInfo) {
		String failMsg = "Expected sorted array [1, 3, 5, 7, 9] but got a different one instead.";
		assertSafely(() -> {
			assertArrayEquals(new Integer[] {1, 3, 5, 7, 9 }, hw.getSortedArray());
			pointsEarned = POINTS_PER_TEST;
		}, failMsg);
	}
	
	@Test
	@DisplayName("main prints the number input by the user")
	public void testMain(TestInfo testInfo) {
		String failMsg = "Did not print the input number.";
		
		// Set up input stream
		int inputNumber = 42;
		ByteArrayInputStream in = new ByteArrayInputStream(String.valueOf(inputNumber).getBytes());
		
		// Set up output stream
		ByteArrayOutputStream readableOutputStream = new ByteArrayOutputStream();
		PrintStream printableOutputStream = new PrintStream(readableOutputStream);
		System.setOut(printableOutputStream);
		
		assertSafely(() -> {
			System.setIn(in);
			// Surround in try/catch/finally to ensure we always set System.out back to original.
			try {
				ExampleHw.main(null);
			} catch(Exception | Error e) {
				throw e;
			} finally {
				System.setOut(originalOut);
			}
			/*
			 *  Caution: This example would assert true any output that contains the number 42.
			 *  That is, an output of 8423 would be marked as correct.
			 *  Ideally, you would have a more thorough check. Using regexes would be a good idea.
			 */
			assertTrue(readableOutputStream.toString().contains(String.valueOf(inputNumber)));
			pointsEarned = POINTS_PER_TEST;

		}, failMsg);
	}
	
	/*
	 * 
	 * 
	 * No more tests below this point
	 * 
	 * 
	 */
	
	private void assertSafely(Runnable x, String failMsg) {
		try {
			assertTimeoutPreemptively(TEST_TIMEOUT, () -> {
				x.run();
			});
		} catch(Exception | Error e) {
			// Identify whether the program crashed or simply had wrong output
			if(!(e instanceof AssertionError)) {
				testOut.println("\tProgram crashed due to a " + e.getClass().getName());
				testOut.println("\t(" + e.getClass().getName() + ") " + e.getMessage());
			} else
				testOut.println("\t" + failMsg);
			
			throw e;
		} finally {
			// Print success if earned all points.
			if(pointsEarned == POINTS_PER_TEST)
				testOut.println("\tSuccess!");
			grade += pointsEarned;
		}
	}

	
	/**
	 * This private class prevents program exiting from System.exit() calls in student's code.
	 */
	private static class NoExitSecurityManager extends SecurityManager {
		
        @Override
        public void checkPermission(Permission perm) {
            // allow anything.
        }
        @Override
        public void checkPermission(Permission perm, Object context) {
            // allow anything.
        }
        @Override
        public void checkExit(int status) 
        {
            super.checkExit(status);
            throw new ExitException(status);
        }
	 }
	 
	 protected static class ExitException extends SecurityException {
		private static final long serialVersionUID = -8576748019682914998L;
		public final int status;
        public ExitException(int status) {
        	System.out.println("System.exit(" + String.valueOf(status) + ")");
	        this.status = status;
        }
    }
}
