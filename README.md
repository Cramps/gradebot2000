# [GradeBot 2000][trope]
A handy tool with a [satirical name][trope] that can automate the grading process of Java programming assignments using JUnit.

## Input
- Directory with zipped student submissions

- (-t) Path to a directory containing JUnit tests (include gradebot2000.jar in directory if using Gradebot2000 Java API)

- (-c) Name of class containing test cases, including namespace (e.g., gradebot2000.example.ExampleHWRegularScoring)

- (-j) JUnit Standalone JAR file (may be skipped if the JAR is included in the tests directory -t)

- (-s) [Optional] Supporting files (e.g, assignment-related java files that students are not supposed to modify)

## Output
- Feedback files with successful and failed test cases for each student
- A list of all students' grades

## Example
To grade the provided example assignments:

```bash
./gradebot2000.py path/to/example/assignments -t path/to/GradingExamples/gradebot2000/examples/ -s example_support/ -c gradebot2000.examples.ExampleHWRegularScoring
```

[trope]: https://tvtropes.org/pmwiki/pmwiki.php/Main/Trope2000