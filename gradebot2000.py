#!/usr/bin/env python3
import os, re
import math, time
import argparse
import shutil, tempfile
import zipfile
import subprocess
from student import Student 
from test_context import TestContext

ASSIGNMENT_TOTAL_POINTS = 100
INSTRUCTOR_TESTS_POINTS = 100

JUNIT_JAR = '!UNSET'
TEST_CONTEXT = TestContext

# This regex MUST match the student's full name and the submission file name.
# Submission [file] name as uploaded by the user, before modified by the submission website/platform.
FILENAME_PATTERN=None

HW_NAME = None
OUT_DIR = None
OUT_FILE = None


def grade(students_list):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_file = open(OUT_FILE, 'w+')

    for student in students_list:
        # create student-specific output file
        student_out_file = open(os.path.join(OUT_DIR, student.full_name + '-' + HW_NAME + '.txt'), 'w+')
        student_out_file.write(student.full_name + '\n\n')

        if student.submitted_correctly:
            # clean current test dir src
            clean_directory(TEST_CONTEXT.SUT_PACKAGE_PATH)
            clean_directory(os.path.join(TEST_CONTEXT.SUT_PATH, 'bin'))
            clean_directory(os.path.join(TEST_CONTEXT.TEST_PATH, 'bin'))

            try:
                # extract student's code
                student.extract(TEST_CONTEXT.SUT_PACKAGE_PATH)

                # compute and output grades
                grade = student.compute_grade(TEST_CONTEXT)
                print(student.full_name + " scored a " + str(grade) + " out of " + str(INSTRUCTOR_TESTS_POINTS) + ' pts.')
                if grade == Student.GRADE_UNGRADED:
                    print("student hasn't been graded")
                elif grade == Student.GRADE_COMPILE_ERROR:
                    student_out_file.write('Your submission could not compile properly.\n\nCOMPILATION ERROR\n\n')
                    student_out_file.write(student.outcome_compilation.stdout.decode("utf-8"))
                elif grade == Student.GRADE_RUNTIME_ERROR:
                    student_out_file.write('Your submission ran into an error at runtime.\nRUNTIME ERROR\n\n')
                    student_out_file.write(student.outcome_junit.stdout.decode("utf-8"))
                elif grade == Student.GRADE_UNKNOWN_ERROR:
                    student_out_file.write('An error occurred while testing your code.')
                elif grade >= 0:
                    student_out_file.write('You scored a ' + str(student.grade) + ' out of ' + str(INSTRUCTOR_TESTS_POINTS) + ' pts.')
                    student_out_file.write('\n\nTEST CASES\n\n')
                    student_out_file.write(student.outcome_junit.stdout.decode("utf-8"))
                # overview log file
                out_file.write(student.full_name + '\t' + str(student.grade) + '\n')
            except zipfile.BadZipFile as e:
                #log badzipfile
                print(e)
            except Exception as e:
                print(e)
    out_file.close()
    
def get_students(path):
    students_submissions_list = os.listdir(path)
    students_list = []
    for submission in students_submissions_list:
        if(not submission.endswith('.zip') or os.path.isdir(submission)):
            continue
        try:
            students_list.append(Student(submission))
        except Exception as e:
            print(type(e))
            print(e)

    return students_list

def clean_directory(directory):
    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def main():
    # Parse command-line options
    if JUNIT_JAR == '!UNSET':
        raise RuntimeError('\033[91mPath to JUnit has not been set. Open grading.py and set it.\033[0m')
    parser = argparse.ArgumentParser(description="Let's grade!")
    parser.add_argument('students_path', default='./', nargs='?')
    parser.add_argument('system_under_test_path')
    parser.add_argument('-t', '--testpath')
    parser.add_argument('-o', '--outdir')
    parser.add_argument('-a', '--hwname')
    parser.add_argument('-c', '--testclass', help='Class name with JUnit test cases')
    parser.add_argument('-s', '--support_path', help='Files in this path will be included in the test. Use this to provide include files provided to, but not modified by, the students.')
    args = parser.parse_args()

    # Set paths
    global TEST_CONTEXT, OUT_DIR
    TEST_CONTEXT.JUNIT_JAR = JUNIT_JAR
    TEST_CONTEXT.SUT_PATH = args.system_under_test_path
    TEST_CONTEXT.SUT_PACKAGE_PATH = os.path.join(args.system_under_test_path, 'src/')
    TEST_CONTEXT.TEST_PATH = args.testpath
    TEST_CONTEXT.ASSIGNMENT_TOTAL = ASSIGNMENT_TOTAL_POINTS
    TEST_CONTEXT.TEST_CLASS = args.testclass
    Student.STUDENTS_PATH = args.students_path
    Student.FILENAME_PATTERN = FILENAME_PATTERN
    OUT_DIR = args.outdir

    if args.support_path:
        TEST_CONTEXT.SUPPORT_PATH = args.support_path

    global HW_NAME
    if not args.hwname:
        HW_NAME = list(filter(None,args.system_under_test_path.split('/')))[-1]
    else:
        HW_NAME = args.hwname

    if not OUT_DIR: # if output directory name was not explicitly given, generate one
        OUT_DIR = 'grades_' + HW_NAME.replace(' ', '_') + '_' + str(math.floor(time.time()))

    global OUT_FILE
    OUT_FILE = os.path.join(OUT_DIR,'grades.log')

    students_list = get_students(args.students_path)
    students_list = [student for student in students_list if student.submitted_correctly]

    grade(students_list)

def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if re.match(name, f):
                result.append(os.path.join(root, f))
    return result

if __name__ == '__main__':
    main()