import geoiq
import unittest

import sys
from geoiq.tests.compare import DeepCompare
from geoiq.tests.functional import *


class TestMapClone(GeoIQFuncTest):

    def test_clone_map(self):
        gq_map = self.random_obj(self.geocommons.maps, 
                                 filt=(lambda x:len(x.layers) > 1),
                                 max_attempts=50).next()
        nmap = self.geoiq.maps.create()
        nmap.copy_from(gq_map)
        
        for (k,v) in nmap.to_json_obj().iteritems():
            print("MAP: %s - %s" % (k,repr(v)))

        nmap.save()
        final_map = self.geoiq.maps.get_by_id(nmap.geoiq_id)
        
        dc = DeepCompare()
        ok,r = dc.compare(final_map.props,gq_map.props)
        dc.pprint(r,outp=sys.stdout)

if (__name__ == "__main__"):
    unittest.main()
