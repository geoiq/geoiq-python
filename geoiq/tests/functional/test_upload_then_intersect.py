import unittest
from geoiq.tests.functional import *


class TestUploadThenIntersect(GeoIQFuncTest):
    def test_upload_then_intersect(self):
        self.geoiq.analysis.load_all_analyses()
        test = self.conf["test_upload_then_intersect"]
        poly_layer = self.geoiq.datasets.create(test["polys"])
        poly_layer.title = "Polygons for upload-then-intersect test"
        poly_layer.save()
        
        points_layer = self.geoiq.datasets.create(test["points"])
        points_layer.title = "Points for upload-then-intersect test"
        points_layer.save()

        fin = self.geoiq.analysis.analyze_intersect(ds1=points_layer.geoiq_id,
                                                    ds2=poly_layer.geoiq_id,
                                                    merge="combine")
        
        self.assertTrue(fin is not None)
        print("Intersected title: %s" % fin.title)

if (__name__ == "__main__"):
    GeoIQTestConf.use_suite("geocommons.com (shoutis)")
    unittest.main()
