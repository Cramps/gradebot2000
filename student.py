import os, re
import subprocess, zipfile, shutil
import tempfile
from test_context import TestContext

class Student:
    GRADE_UNGRADED = 'UNGRADED' # Starting value for every student's grade attribute.
    GRADE_COMPILATION_ERROR = 'COMPILATION ERROR'
    GRADE_RUNTIME_ERROR = 'RUNTIME ERROR' # No tests executed. Perhaps due to an incorrect student submission.
    GRADE_UNKNOWN_ERROR = 'UNKNOWN ERROR' # Undetermined error. Look at logs!
    FILENAME_PATTERN = None
    STUDENTS_PATH = None

    def __init__(self, file_name):
        TestContext.log('Creating student for ' + file_name)
        self.file_name = file_name
        self.full_name = None
        self.grade = Student.GRADE_UNGRADED
        self.total_assignment_points = None

        self.extracted = False
        self.extracted_path = None
        self.outcome_compilation = None

        self.out_file = None

        self.submitted_correctly = False # assume false until proven true
        self.verify_submission() # check if submitted correctly

    def verify_submission(self):
        TestContext.log('Verifying submission for ' + self.file_name)
        if Student.FILENAME_PATTERN:
            try:
                regex = re.compile(Student.FILENAME_PATTERN, re.IGNORECASE)
                result_regex_match = regex.match(self.file_name)
                self.full_name = result_regex_match.group(1)
                self.submitted_correctly = True
            except AttributeError as e:
                raise AttributeError("File does not match student submission filename pattern. (" + self.file_name + ").")
            except Exception as e:
                TestContext.log("Unexpected exception!",1)
                TestContext.log(e,1)
        elif re.match("^.*\.zip", self.file_name):
            self.submitted_correctly = True


    def extract(self, path=None):
        TestContext.log('Extracting ' + self.file_name + (' (' + self.full_name + ')' if self.full_name else '') + '...')
        try:
            with zipfile.ZipFile(os.path.join(Student.STUDENTS_PATH, self.file_name)) as submission_file:
                with path if path else tempfile.TemporaryDirectory() as extract_path:
                    submission_file.extractall(extract_path)
                    self.extracted_path = extract_path
                    self.extracted = True
            
        except zipfile.BadZipFile as e:
            TestContext.log('Failed to extract ' + self.file_name, 1)
            TestContext.log(e,1)
            raise zipfile.BadZipFile("File " + self.file_name + " is not a zip file.")

    def include_support_files(self, context):
        TestContext.log('Including support files...')
        try:
            Student.copytree(context.SUPPORT_PATH, self.extracted_path)
        except Exception as e:
            TestContext.log('Could not include support files.', 1)
            TestContext.log(e,1)
            raise e

    def include_test_files(self, context):
        TestContext.log('Including test files...')
        try:
            Student.copytree(os.path.join(context.TEST_PATH), self.extracted_path)
        except Exception as e:
            TestContext.log('Could not include test cases.', 1)
            TestContext.log(e, 1)
            raise e

    # find all .java files to compile
    # TO-DO: Make this platform-independent...
    def compile_code(self, context):
        TestContext.log('Compiling ' + self.id())
        tmp_token, tmp_path = tempfile.mkstemp(prefix='grading_')
        subprocess.run("find " + self.extracted_path + ' \( -iregex "\/[^\.]*\.java" ! -path "*__MACOSX*" \) > ' + tmp_path, shell=True)

        # compile files
        compilation_output_path = os.path.join(self.extracted_path, 'bin')
        if not os.path.exists(compilation_output_path):
            os.makedirs(compilation_output_path)
        class_path = context.JUNIT_JAR + ':' + os.path.join(self.extracted_path,'gradebot2000.jar')

        self.outcome_compilation = subprocess.run("javac -classpath " + class_path + " -encoding " + context.ENCODING + " -d " + compilation_output_path + ' @' + tmp_path, shell=True, capture_output=True)
        os.remove(tmp_path)

    # run java -cp .:/usr/share/java/junit.jar org.junit.runner.JUnitCore MyTests > gradeFile
    # java -ea -jar /path/to/junit-platform-console-standalone-1.3.1.jar -cp /path/to/compiled/files/:gradebot2000.jar --include-classname='.*' -c gradebot2000.samples.SampleHWRegularScoring 
    def run_junit_test_cases(self, context):
        if self.extracted:
            TestContext.log('Running test cases...')
            options = " --config=junit.platform.output.capture.stdout=true --config=junit.platform.output.capture.stderr=true"
            class_path =os.path.join(self.extracted_path,'gradebot2000.jar') + ':' + os.path.join(self.extracted_path, 'bin')
            self.outcome_junit = subprocess.run("java -ea -jar " + context.JUNIT_JAR + " -cp " + class_path + " --include-classname='.*' -c " + context.TEST_CLASS, shell=True, capture_output=True)

            self.grade, self.total_assignment_points = self.parse_grade(context, self.outcome_junit.stdout.decode("utf-8"))
        else:
            TestContext.log('Cannot run test cases for unzipped file ' + self.file_name)

    # Parses jUnit output to get grade and total assignment points
    def compute_grade(self, context):
        TestContext.log('Computing grade for ' + self.file_name)
        if not self.extracted:
            self.extract()
        if self.extracted:
            if context.SUPPORT_PATH:
                self.include_support_files(context)

            if context.TEST_PATH:
                self.include_test_files(context)

            else:
                raise AttributeError("No test cases found!") #Should never happen

            try:
                self.compile_code(context)
                if self.outcome_compilation and self.outcome_compilation.returncode != 0:
                    self.grade = Student.GRADE_COMPILATION_ERROR
                    return self.grade

                self.run_junit_test_cases(context)
                if self.outcome_junit and self.outcome_junit.stderr.decode("utf-8") != '':
                    self.grade = Student.GRADE_RUNTIME_ERROR
                    return self.grade

            except AttributeError as e:
                self.grade = Student.GRADE_UNKNOWN_ERROR
                TestContext.log(e,1)
                raise AttributeError(self.file_name + ' - ' + 'This is not a proper student assignment!')
            except Exception as e:
                self.grade = Student.GRADE_UNKNOWN_ERROR
                TestContext.log(e,1)
                raise e

            TestContext.log(self.id() + " scored a " + str(self.grade) + ' out of ' + str(self.total_assignment_points) + ' pts')
            return self.grade

    def id(self):
        return self.full_name if self.full_name else self.file_name

    def output(self, out_dir):
        self.out_file = os.path.join(out_dir, self.id() + (' - ' + TestContext.HW_NAME if TestContext.HW_NAME else '') + '.txt')
        if self.grade != Student.GRADE_UNGRADED:
            with open(self.out_file,'w+') as out_file:
                out_file.write(self.id() + '\n\n')

                if self.grade == Student.GRADE_COMPILATION_ERROR:
                    out_file.write('Your submission could not compile properly.\n\nCOMPILATION ERROR\n\n')
                    out_file.write(self.outcome_compilation.stdout.decode("utf-8"))
                    out_file.write(self.outcome_compilation.stderr.decode("utf-8"))
            
                elif self.grade == Student.GRADE_RUNTIME_ERROR:
                    out_file.write('Your submission ran into an error at runtime.\nRUNTIME ERROR\n\n')
                    out_file.write(self.outcome_junit.stdout.decode("utf-8"))
                    out_file.write(self.outcome_junit.stderr.decode("utf-8"))

                elif self.grade == Student.GRADE_UNKNOWN_ERROR:
                    out_file.write('An error occurred while testing your code.')

                elif float(self.grade) >= 0:
                    out_file.write('You scored a ' + str(self.grade) + ' out of ' + str(self.total_assignment_points) + ' pts.')
                    out_file.write('\n\nTEST CASES\n\n')
                    out_file.write(self.feedback if self.feedback else '')

    def remove_package_declaration(old_path):
        pattern = r"^\s*package .*;"
        tmp_token, tmp_path = tempfile.mkstemp()
        with os.fdopen(tmp_token,'w') as new_file:
            with open(old_path) as old_file:
                for line in old_file:
                    new_file.write(re.sub(pattern, '', line))
        os.remove(old_path)
        shutil.move(tmp_path, old_path)

    def copytree(src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    shutil.copy2(s, d)

    def parse_grade(self, context, test_output):
        try:
            pts_from_tests = re.findall(r"(You scored a (\d+\.?\d+) out of (\d+\.?\d+))", test_output)
            if len(pts_from_tests) > 0:
                self.feedback = test_output[:test_output.rfind(pts_from_tests[-1][0])]
                return float(pts_from_tests[-1][1]), float(pts_from_tests[-1][2]) 
            else:
                return Student.GRADE_RUNTIME_ERROR, None
            
        except Exception as e:
            TestContext.log('Failed to parse grades after running test cases for ' + self.file_name, 1)
            TestContext.log(e,1)
            return Student.GRADE_UNKNOWN_ERROR, None

