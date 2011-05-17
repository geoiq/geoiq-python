import geoiq,sys
import unittest
from geoiq.tests.functional import *


class TestSearch(GeoIQFuncTest):
    def t_imp(self, endpoint):
        rs = list(endpoint.geoiq.search("",model=endpoint,max_results=1))
        #r = list(self.random_obj(endpoint))
        if (len(rs) == 0):
            sys.stderr.write("WARNING: NO RESULTS\n")
            return
        r = rs[0].load()
        self.assertTrue(r.svc is endpoint)
        
    def test_map_search(self):
        self.t_imp(self.geoiq.maps)

    def test_ds_search(self):
        self.t_imp(self.geoiq.datasets)

    def test_analysis_search(self):
        self.t_imp(self.geoiq.analysis)

        
        

if (__name__ == "__main__"):
    unittest.main()
