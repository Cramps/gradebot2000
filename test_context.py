import sys

class TestContext:
    JUNIT_JAR = None
    TEST_PATH = None
    TEST_CLASS = None
    ASSIGNMENT_TOTAL = None
    SUT_PATH = None
    SUT_PACKAGE_PATH = None
    SUPPORT_PATH = None
    HW_NAME = None
    ENCODING = 'utf8'

    LOGGING = False

    def log(msg, type=0):
        if type == 0:
            if TestContext.LOGGING:
                print('\n' + str(msg))
        if type == 1:
            sys.stderr.write('\n' + str(msg.args[0]))






