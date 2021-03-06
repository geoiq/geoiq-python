#

__all__ = [ "GeoIQFuncTest", "GeoIQTestConf" ]

import functesting
import geoiq
import unittest, os, os.path, random, tempfile

try:
    import simplejson as json
except ImportError:
    import json

class GeoIQSteps(object):
    @functesting.step()
    def search(self,g,*args,**kwargs):
        return g.search.search_raw(*args,**kwargs)

    @functesting.step()
    def first_and_last(self,g, *args,**kwargs):
        nargs = dict(kwargs)
        nargs['per_page'] = 1
        nargs['page_limit'] = 1
        nargs['start_page'] = 0
        frontpage = list(self.search(g,*args,**nargs))[0]
        res = frontpage.totalResults
        nargs['start_page'] = res

        lastpage = list(self.search(g,*args,**nargs))
        lastpage = lastpage[0]
        return (frontpage.entries[0],lastpage.entries[0])

    @functesting.step()
    def random_obj(self,endpoint, filt=None,numwanted=1, max_attempts = 10):
        gq = endpoint.geoiq
        ids = [r.key for r in self.first_and_last(gq,"*",model=endpoint)]
        ids.sort()
        st,nd = ids

        if filt is None: filt = lambda x:True

        fail_count = 0
        count = 0
        while count < numwanted and fail_count < max_attempts:
            rid = random.randint(st,nd)
            try:
                r = endpoint.get_by_id(rid)
                if (r is not None) and filt(r):
                    yield r
                    count += 1
                else: 
                    print("filtered/404 %d, %r" % (rid,r))
                    fail_count += 1
            except geoiq.geoiq.GeoIQAccessDenied,err:
                fail_count += 1
                print("Access denied (%d) - %s" % (rid, str(err)))


class GeoIQTestConf(object):
    suite_name = None

    def __init__(self):
        self.geocommons = geoiq.GeoIQ()
        conf = os.path.join(os.getcwd(), "testconf.json")
        if not os.path.exists(conf):
            conf = os.path.join(os.getcwd(),"bin", "testconf.json")
        if not os.path.exists(conf):
            raise ValueError("Missing testconf.json!")

        c = open(conf)
        self.conf = json.load(c)
        c.close()

        if (GeoIQTestConf.suite_name is not None):
            self.conf.update(self.conf["suite"][GeoIQTestConf.suite_name])

        self.geoiq = geoiq.GeoIQ(self.conf.get("root"),
                                 self.conf.get("username"),
                                 self.conf.get("password"),
                                 self.conf.get("apiver"))
    @classmethod
    def use_suite(cls, nm):
        cls.suite_name = nm


class GeoIQFuncTest(functesting.FuncTest, GeoIQSteps):
    def setUp(self):
        c = GeoIQTestConf()
        self.geoiq = c.geoiq
        self.geocommons = c.geocommons
        self.conf = c.conf



    def working_folder(self):
        scratch = self.conf.get("workdir","scratch")
        td = tempfile.mkdtemp(dir=scratch,suffix=".wkdir")
        
        # TODO: register for cleanup?
        
        return td
        
