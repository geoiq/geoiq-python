from geoiq.tests.functional import *

import unittest as ut
import time,sys, StringIO
try:
    import simplejson as json
except ImportError:
    import json
import urllib
most_recent_socket = None

class FuncTestResult(ut.TestResult):
    def __init__(self):
        ut.TestResult.__init__(self)
        self.successes = []
        self.all_tests = []

    def getDescription(test):
        return str(test)
        #return test.shortDescription() or str(test)

    def startTest(self, test):
        global rout
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        rout.write("/* Starting %s */\n" % str(test))
        rout.flush()
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
        global most_recent_socket
        self.curtest["stdout"] = sys.stdout.getvalue()
        self.curtest["stderr"] = sys.stderr.getvalue()
        self.curtest["stoptime"] = time.time()
        sz = 1024 * 16
        if most_recent_socket is not None:
            self.curtest["last_written"] = urllib.quote(
                most_recent_socket._send_log.getvalue()[:sz]
                )
            self.curtest["last_read"] = urllib.quote(
                most_recent_socket._recv_log.getvalue()[:sz]
                )

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


# HACKY: logging socket: an object that,
#  in httplib, is dynamically inserted intead
#  of the socket module.
#==========================
import socket
import StringIO

class proxyit(object):
    def __init__(self, inner, overrides):
        self.inner = inner
        self.overrides = overrides
        overrides.set_inner(inner, self)
        
    def __getattribute__(self, name):
        inner = object.__getattribute__(self, "inner")
        over = object.__getattribute__(self, "overrides")
        r = getattr(over, name, None)
        if r is not None and name != "set_inner": return r
        return getattr(inner, name)

class logged_socket(object):
    def __init__(self):
        global most_recent_socket
        self._send_log = StringIO.StringIO()
        self._recv_log = StringIO.StringIO()
        most_recent_socket = self

    def set_inner(self, i, p): 
        self.socket = i
        self.proxy = p

    def recv(self,*args, **kargs):
        r = self.socket.recv(*args,**kargs)
        self._recv_log.write(r)
        return r

    def recvfrom(self, *args, **kargs):
        ra, rb = self.socket.recvfrom(buf,*args,**kargs)
        self._recv_log.write(ra)
        return (ra,rb)

    def recv_into(self, buf, *args, **kargs): 
        rcount = self.socket.recv_into(buf,*args,**kargs)
        self._recv_log.write(buf[:rcount])
        return rcount

    def recvfrom_into(self): 
        rcount,rb = self.socket.recv_into(buf,*args,**kargs)
        self._recv_log.write(buf[:rcount])
        return (rcount,rb)

    def send(self,dat,*args,**kargs):
        self._send_log.write(dat)
        return self.socket.send( dat, *args, **kargs)

    def sendall(self,dat,*args,**kargs):
        self._send_log.write(dat)
        return self.socket.sendall( dat, *args, **kargs)

    def sendto(self,dat,*args,**kargs):
        self._send_log.write(dat)
        return self.socket.sendto( dat, *args, **kargs)

    def makefile(self,*args,**kargs):
        res = logged_socket_file(self.socket._sock, *args, **kargs)
        res._set_logs(self._send_log, self._recv_log)
        return res

class logged_socket_file(socket._fileobject):
    def _set_logs(self, sendlog, recvlog):
        self._send_log = sendlog
        self._recv_log = recvlog

    def write(self, data):
        self._send_log.write(data)
        return socket._fileobject.write(self, data)
    def writelines(self, lines):
        self._send_log.write("".join(filter(None,map(str,list))))
        return socket._fileobject.writelines(self,lines)

    def read(self, *args, **kargs):
        r = socket._fileobject.read(self,*args,**kargs)
        self._recv_log.write(r)
        return r

    def readline(self, *args, **kargs):
        r = socket._fileobject.readline(self,*args,**kargs)
        self._recv_log.write(r)
        return r
    

def wrap_createconnection(*args, **kargs):
    return proxyit(socket.create_connection(*args,**kargs), logged_socket())

def wrap_socket(*args, **kargs):
    return proxyit(socket.socket(*args,**kargs), logged_socket())

class SocketTracingHack(object):
    def __getattribute__(self, nm):
        if (nm == "create_connection"): return wrap_createconnection
        if (nm == "socket"): return wrap_socket
            
        return getattr(socket, nm)

#====================


if (__name__ == '__main__'):
    import httplib
    httplib.socket = SocketTracingHack()

    # Import all tests here...
    from test_users import *
    #from test_dataset_clone import *
    #from test_map_clone import *
    from test_dataset import *
    from test_analysis import *
    from test_search import *
    from test_upload_then_intersect import *

    rout = sys.stdout
    # http://mail.python.org/pipermail/tutor/2005-November/043069.html
    # TODO!: breaks multipart/form-encoded.....
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
        # if name != "geocommons.com (shoutis)": continue

        rout.write("/* suite %s ... */\n" % (name))
        GeoIQTestConf.use_suite(name)
        tr = FuncTestRunner()

        ut.TestProgram(testRunner = tr)



    sys.exit = oexit
    sys.stdout.write("testResults(")
    sys.stdout.write(json.dumps(list(FuncTestRunner.alltests), ensure_ascii=True))
    sys.stdout.write(");")
    sys.exit(all(t["status"] == "success" for t in FuncTestRunner.alltests))
