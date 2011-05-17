import geoiq
import unittest
from geoiq.tests.functional import *
import sys

class DatasetTests(GeoIQFuncTest):

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
        

    def test_ds_features(self):
        tests = self.conf.get("test_features")
        if (tests is None):
            sys.stderr.write("WARNING: Can't test_features without a dataset in testconf.json")
            return

        for test in tests:
            ds = self.geoiq.datasets.get_by_id(test["id"])

            self.assertEquals(ds.title, test["expected_title"])
            self.assertEquals(ds.feature_count, test["expected_count"])
        
            feats = list(ds.features())
            self.assertEquals(len(feats), test["expected_count"])
        

if (__name__ == "__main__"):
    unittest.main()
