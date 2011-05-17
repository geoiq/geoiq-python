import geoiq
import unittest
from geoiq.tests.functional import *


class TestDataset(GeoIQFuncTest):

        

    def imp_test_up(self, nm):
        sf = self.conf.get(nm)
        if sf is None :
            print("Skipping: no " + nm)
            return

        ds = self.geoiq.datasets.create(sf)
        ds.title = "Test creation: " + nm
        ds.save()
        fin = ds.geoiq_id

        dd = self.geoiq.datasets.get_by_id(fin)
        self.assertEquals(dd.title, ds.title)
        return ds

    def test_upload_shapefile(self):
        self.imp_test_up("shapefile")
    def test_upload_kml(self):
        self.imp_test_up("kmlfile")
        

if (__name__ == "__main__"):
    unittest.main()
