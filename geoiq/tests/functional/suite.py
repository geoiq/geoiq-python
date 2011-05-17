from geoiq.tests.functional import *

import unittest as ut
import time,sys, StringIO
try:
    import simplejson as json
except ImportError:
    import json

class FuncTestResult(ut.TestResult):
    def __init__(self):
        ut.TestResult.__init__(self)
        self.successes = []
        self.all_tests = []

    def getDescription(test):
        return str(test)
        #return test.shortDescription() or str(test)

    def startTest(self, test):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        self.curtest = {}
        self.curtest["starttime"] = time.time()
        self.curtest["test"] = test.shortDescription() or str(test)
        self.curtest["suite"] = GeoIQTestConf.suite_name
        self.curtest["pyver"] = sys.version
        self.curtest["module"] = test.__module__

        return ut.TestResult.startTest(self,test)
    
    def stopTest(self, test):
        self.curtest["stdout"] = sys.stdout.getvalue()
        self.curtest["stderr"] = sys.stderr.getvalue()
        self.curtest["stoptime"] = time.time()
        self.all_tests.append(self.curtest)
        self.curtest = None

        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        return ut.TestResult.stopTest(self,test)

    def addSuccess(self, test):
        self.curtest["status"] = "success"
        self.successes.append(test)

    def addFailure(self, test, err):
        self.curtest["status"] = "failure"
        self.curtest["exception"] = self._exc_info_to_string(err,test)
        return ut.TestResult.addFailure(self,test,err)

    def addError(self, test, err):
        self.curtest["status"] = "error"
        self.curtest["exception"] = self._exc_info_to_string(err,test)
        return ut.TestResult.addError(self,test,err)

class FuncTestRunner:
    alltests = []

    def __init__(self):
        pass
    
    def run(self, test):
        startTime = time.time()
        result = FuncTestResult()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        FuncTestRunner.alltests.extend(result.all_tests)


        #if not result.wasSuccessful():
         #   self.stream.write("FAILED....\n")
        return result

if (__name__ == '__main__'):
    # Import all tests here...
    from test_users import *
    from test_dataset_clone import *
    from test_map_clone import *
    from test_dataset import *
    from test_analysis import *

    # http://mail.python.org/pipermail/tutor/2005-November/043069.html
    # TODO: breaks multipart/form-encoded..
    #import urllib2
    #h = urllib2.HTTPHandler(debuglevel=1)
    #opener = urllib2.build_opener(h)
    #urllib2.install_opener(opener)

    #httplib.HTTPConnection.debuglevel = 1

    # Some ugly hackery here... want to run tests multiple times w/ dif
    #  configs, so we'll just monkeypatch sys.exit
    def nexit(code):
        pass
    oexit = sys.exit
    sys.exit = nexit

    testconf = GeoIQTestConf()

    for (name,conf) in testconf.conf["suite"].iteritems():        
        GeoIQTestConf.use_suite(name)
        tr = FuncTestRunner()

        ut.TestProgram(testRunner = tr)

    sys.exit = oexit
    sys.stdout.write("testResults(")
    sys.stdout.write(json.dumps(list(FuncTestRunner.alltests)))
    sys.stdout.write(");")
    sys.exit(all(t["status"] == "success" for t in FuncTestRunner.alltests))
