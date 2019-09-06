#!/usr/bin/env python3
import os, re
import math, time
import argparse
import shutil, tempfile
import zipfile
import subprocess
from student import Student 
from test_context import TestContext

FILENAME_PATTERNS= {
    'cofc': r"^\d+-\d+ - ([\w\s\-']+)- \w\w\w{1,2} \d+, \d{4} \d+ [APM]{2} - ([\w\s\-]+\.zip)",
    'example': r"ExampleHW - (.*)\.zip" }

HW_NAME = None
OUT_DIR = None
OUT_FILE = None

def grade(students_list):
    os.makedirs(OUT_DIR, exist_ok=True)
    
    with open(OUT_FILE, 'w+') as out_file:
        TestContext.log('Opening out_file...')
        for student in students_list:
            TestContext.log('Grading ' + student.id() + '...')
            student.compute_grade(TestContext)
            TestContext.log('Output grade for ' + student.id() + '...')
            student.output(OUT_DIR)
            TestContext.log('Output grade for ' + student.id() + '...')
            out_file.write(student.id() + '\t' + str(student.grade) + '\n')
        
def get_students(path):
    students_submissions_list = os.listdir(path)
    students_list = []
    for submission in students_submissions_list:
        if(not submission.endswith('.zip') or os.path.isdir(submission)):
            continue
        students_list.append(Student(submission))

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
            TestContext.log(e,1)

def main():

    # Parse command-line options
    parser = argparse.ArgumentParser(prog='Gradebot 2000', description="Let's grade!")
    parser.add_argument('students_path', default='./', nargs='?')
    parser.add_argument('-t', '--testspath', '--testpath', required=True)
    parser.add_argument('-c', '--testsclass', '--testclass', required=True, help='Class name with JUnit test cases')
    parser.add_argument('-sp', '--support_path', help='Files in this path will be included in the test. Use this to include files provided to, but not modified by, the students.')
    parser.add_argument('-o', '--outdir', help='Optional. Generates new directory by default.')
    parser.add_argument('-j', '--junit_jar', default=os.environ.get('JUNIT_JAR'), help='If using a different version of JUnit, use this option to set the path to its JAR file.')
    parser.add_argument('-e', '--update_env', action='store_true', help='Add this option to update JUNIT_JAR environment variable with the JAR file provided with --junit_jar (-j).')
    parser.add_argument('-p', '--filename_pattern', '--pattern', choices=['cofc', 'example'], help='Filename patterns (regexes) can help extract student names or IDs from filenames')
    parser.add_argument('-a', '--hwname')
    parser.add_argument('--version', action='version', version='%(prog)s version 1.0.0')
    args = parser.parse_args()

    # Set paths
    global OUT_DIR

    if args.junit_jar and re.match(r'^.*\.jar', args.junit_jar):
        TestContext.log('Verifying JAR file...')
        TestContext.JUNIT_JAR = args.junit_jar
    else:
        TestContext.log('JUnit JAR not provided.')
        junit_jar = os.path.join(args.testspath,'junit-platform-console-standalone-1.3.1.jar')
        TestContext.log('Looking for jar file at ' + junit_jar + '...')
        if os.path.isfile(junit_jar):
            TestContext.JUNIT_JAR = junit_jar
        else:
            raise RuntimeError('\033[91mJUnit not found. You can provide a JAR file using -j option.\033[0m')

    TestContext.TEST_PATH = args.testspath
    TestContext.TEST_CLASS = args.testsclass
    Student.STUDENTS_PATH = args.students_path
    if args.filename_pattern and args.filename_pattern in FILENAME_PATTERNS:
        TestContext.log('Using filename pattern ' + args.filename_pattern + '...')
        Student.FILENAME_PATTERN = args.filename_pattern
    OUT_DIR = args.outdir

    if args.support_path:
        TestContext.log('Using support path ' + args.support_path + '...')
        TestContext.SUPPORT_PATH = args.support_path

    if not args.hwname:
        TestContext.HW_NAME = ''
    else:
        TestContext.HW_NAME = args.hwname

    if not OUT_DIR: # if output directory name was not explicitly given, generate one
        OUT_DIR = 'grades_' + str(math.floor(time.time())) + ('_' + TestContext.HW_NAME.replace(' ', '_') if TestContext.HW_NAME else '')

    global OUT_FILE
    OUT_FILE = os.path.join(OUT_DIR,'grades.log')

    TestContext.log('Looking for students in ' + args.students_path)
    students_list = [student for student in get_students(args.students_path) if student.submitted_correctly]

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