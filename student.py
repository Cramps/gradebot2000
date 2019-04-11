import os, re
import subprocess, zipfile, shutil
import tempfile
class Student:
    # GRADING
    GRADE_UNGRADED = 'UNGRADED' # Starting value for every student's grade attribute.
    GRADE_COMPILE_ERROR = 'COMPILATION ERROR'
    GRADE_RUNTIME_ERROR = 'RUNTIME ERROR' # No tests executed. Perhaps due to an incorrect student submission.
    GRADE_UNKNOWN_ERROR = 'UNKNOWN ERROR' # Undetermined error. Look at logs!
    FILENAME_PATTERN = None
    FILENAME_VERIFICATION_PATTERN = None
    STUDENTS_PATH = None

    def __init__(self, file_name):
        self.file_name = file_name
        self.grade = Student.GRADE_UNGRADED
        self.extracted = False
        self.tmp_token = None
        self.tmp_path = None
        self.submitted_correctly = False # assume false until proven true
        self.verify_submission() # check if submitted correctly

    def verify_submission(self):
        # Match submission and regex once. Match object should capture 2 groups.
        #   group 1 = full name
        #   group 2 = original submission file name
        regex = re.compile(Student.FILENAME_PATTERN, re.IGNORECASE)
        result_regex_match = regex.match(self.file_name)
        try:

            self.full_name = result_regex_match.group(1)
            
            if Student.FILENAME_VERIFICATION_PATTERN:
                submission_name = re.match(FILENAME_VERIFICATION_PATTERN, self.file_name)
                self.submitted_correctly = True if submission_name else False
            else:
                self.submitted_correctly = True
        except AttributeError as e:
            raise AttributeError("File does not match student submission filename pattern. (" + self.file_name + ").")

    def extract(self, path):
        try:
            # print('Unzipping ' + self.full_name + '\'s submission (' + os.path.join(STUDENTS_PATH, self.file_name) + ')...')
            with zipfile.ZipFile(os.path.join(Student.STUDENTS_PATH, self.file_name)) as submission_file:
                submission_file.extractall(path)
                for root, dirs, files in os.walk(path):
                    for file in files:
                        shutil.move(os.path.join(root,file), os.path.join(path,file))
                self.extracted = True
            
        except zipfile.BadZipFile as e:
            # print('Failed to unzip ' + self.full_name + '\'s submission (' + os.path.join(STUDENTS_PATH, self.file_name) + ').', e, '\n')
            raise zipfile.BadZipFile("File " + self.file_name + " is not a zip file.")

    # Parses jUnit output and calculates grade based on points lost
    # For this to work as intended, all assertion statements in jUnit should
    # have an error message with the amount of points lost if the assertion fails.
    def compute_grade(self, context):
        if self.extracted:
            if context.SUPPORT_PATH:
                try:
                    Student.copytree(context.SUPPORT_PATH, context.SUT_PACKAGE_PATH)
                except Exception as e:
                    print(e)
                    pass

            # find all .java files to compile
            tmp_token, tmp_path = tempfile.mkstemp(prefix='grading_')
            try:
                subprocess.run("find " + os.path.join(context.SUT_PATH,'src') + ' \( -iregex "\/[^\.]*\.java" ! -path "*__MACOSX*" \) > ' + tmp_path, shell=True)
                # Remove package declaration from java files
                with open(tmp_path) as files_to_compile:
                    for line in files_to_compile:
                        if line.endswith('.java\n') or line.endswith('.java'):
                            Student.remove_package_declaration(line.strip('\n'))

                # compile files
                # print('\tCompiling ', self.full_name)
                self.outcome_compilation = subprocess.run("javac -classpath " + context.JUNIT_JAR + " -encoding utf8 -d " + os.path.join(context.TEST_PATH, 'bin') + ' @' + tmp_path, shell=True, capture_output=True)
                if self.outcome_compilation.returncode != 0:
                    self.grade = Student.GRADE_COMPILE_ERROR
                    return self.grade

                # run java -cp .:/usr/share/java/junit.jar org.junit.runner.JUnitCore MyTests > gradeFile
                options = " --config=junit.platform.output.capture.stdout=true --config=junit.platform.output.capture.stderr=true"
                class_path = os.path.join(context.TEST_PATH,'bin') + ':' + os.path.join(context.SUT_PATH,'bin')
                self.outcome_junit = subprocess.run("java -ea -jar " + context.JUNIT_JAR + " -cp " + class_path + " --include-classname='.*' -c " + context.TEST_CLASS, shell=True, capture_output=True)

                # parse grades
                self.grade = self.parse_grade(context, self.outcome_junit.stdout.decode("utf-8"))
                
            except AttributeError as e:
                print(e)
                self.grade = Student.GRADE_UNKNOWN_ERROR
                raise AttributeError('This is not a proper student object!')
            except Exception as e:
                print(e)
                self.grade = Student.GRADE_UNKNOWN_ERROR
            finally:
                os.remove(tmp_path)

                return self.grade

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
            pts_from_tests = re.findall(r"You scored a (\d+\.\d+) out of (\d+\.\d+)", test_output)
            if len(pts_from_tests) > 0:
                grade = float(pts_from_tests[-1][0])
            else:
                grade = Student.GRADE_RUNTIME_ERROR
            
            return grade
        except Exception as e:
            print(e)
            return Student.GRADE_UNKNOWN_ERROR

