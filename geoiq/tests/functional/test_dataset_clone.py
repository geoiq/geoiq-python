import geoiq, unittest
from geoiq.tests.functional import *

class TestDatasetClone(GeoIQFuncTest):
    def test_clone_dataset(self):
        gc_ds = self.random_obj(self.geocommons.datasets).next()
        # .. todo

if (__name__ == "__main__"):
    unittest.main()
