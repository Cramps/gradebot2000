package gradebot2000.examples;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.time.Duration;
import java.util.ArrayList;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;

import gradebot2000.GradeBotTest;
import gradebot2000.examples.assignments.ExampleHW;

public class ExampleHWRegularScoring extends GradeBotTest {
	
	@BeforeAll
	static void setUpAll() {
		int totalNumberOfTestCasesINeed = 6;
		
		// === Total points of this assignment ===
		// Option 1. Total points will default to 100 if not provided in the setUp method. (Uncomment next line)
		setUpScoring(totalNumberOfTestCasesINeed);
		
		// Option 2. Provide the total points this assignment is worth. (Uncomment next 2 lines)
		// int totalPoints = 30; // Can use "double" for decimal numbers.
		// setUpScoring(totalNumberOfTestCasesINeed, totalPoints);
		
		/*
		 *  === Tests timeout === (OPTIONAL; default is 5 seconds)
		 *  The default timeout can be changed using the setTimeout(Duration) method.
		 *  
		 *  The setTimeout(Duration) method changes the timeout for ALL test cases.
		 *  For setting the timeout for specific test cases, consider adding the timeout parameter to
		 *  one of the grade(...) methods. For example:
		 *  
		 *  grade(()-> assertTrue(myBoolean, failMsgString), Duration.ofSeconds(10));
		 *  
		 *  The example below changes the timeout to 2 seconds and then resets it to its default value.
		 */
		setTimeout(Duration.ofSeconds(2));
		setTimeout(DEFAULT_TIMEOUT);
		
	}
	
	@Test
	@DisplayName("Insert a number at arbitrary position in the list (except start or end of list)")
	public void testListInsert() throws InterruptedException {
		ArrayList<Integer> list = new ArrayList<>();
		int[] initialContentsOfList = new int[] { 0, 4, 8, 12, 16, 20 };
		for(int i : initialContentsOfList)
			list.add(i);
		
		// Testing the add(index, element) method
		int expected = 42;
		grade(()-> { 
			list.add(4, 42);
			int actual = list.get(4);
			assertEquals(expected, actual);
		});
	}
	
	/*
	 * The GradeBotTest class also includes handy methods such as fileContainsString(filepath, pattern) (used below)
	 * and stringContains(myString, pattern), which return true if the given file or String contain the pattern provided.
	 * 
	 * The pattern can be either a word or a regular expression (regex), but remember to escape characters as necessary!
	 * The example below shows a simple regex pattern. Notice how the backslash has to be escaped.
	 * If using relative paths (like the one below), the project's root folder is where the file search begins.
	 */
	@Test
	@DisplayName("File contains word or pattern")
	public void testFileContainsString() throws InterruptedException {
		grade(()-> {
			assertTrue(fileContainsString("my_file.txt", "CSCI-\\d{3}"));
		});
	}
	
	
	/*
	 *  The main() method takes user input and will stop execution until this input is provided.
	 *  We provide an input using an InputStream.  
	 */
	@Test
	@DisplayName("main() prints the number input by the user")
	public void testMain(TestInfo testInfo) {
		String failMsg = "Did not print the input number.";
		
		// Set up input stream
		int inputNumber = 42;
		ByteArrayInputStream in = new ByteArrayInputStream(String.valueOf(inputNumber).getBytes());
		
		// Set up output stream
		ByteArrayOutputStream readableOutputStream = new ByteArrayOutputStream();
		PrintStream printableOutputStream = new PrintStream(readableOutputStream);
		System.setOut(printableOutputStream);
		
		grade(() -> {
			System.setIn(in);
			// Surround in try/catch/finally to ensure we always set System.out back to original.
			try {
				ExampleHW.main(null);
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
			assertTrue(readableOutputStream.toString().contains(String.valueOf(inputNumber)), failMsg);
		});
	}
	
	@Test
	@DisplayName("isSorted() returns true when sorted")
	public void testIsSorted(TestInfo testInfo) {
		String failMsg = "Returned false when expected true.";
		grade(() -> {
			ExampleHW hw = new ExampleHW(new Integer[] { 1, 3, 5, 7, 9 });
			assertTrue(hw.isSorted(), failMsg);
		});
	}
	
	@Test
	@DisplayName("isSorted() returns false when unsorted")
	public void testIsNotSorted(TestInfo testInfo) {
		String failMsg = "Returned true when expected false.";
		grade(() -> {
			ExampleHW hw = new ExampleHW(new Integer[] { 5, 3, 9, 1, 7 });
			assertFalse(hw.isSorted(), failMsg);
		});
	}
	
	@Test
	@DisplayName("getSortedArray returns the sorted array")
	public void testGetSortedArray(TestInfo testInfo) {
		String failMsg = "Expected sorted array [1, 3, 5, 7, 9] but got a different one instead.";
		grade(() -> {
			ExampleHW hw = new ExampleHW(new Integer[] { 5, 3, 9, 1, 7 });
			assertArrayEquals(failMsg, new Integer[] {1, 3, 5, 7, 9 }, hw.getSortedArray());
		});
	}
}