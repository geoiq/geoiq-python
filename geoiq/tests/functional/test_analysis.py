import unittest
from geoiq.tests.functional import *


class TestDataset(GeoIQFuncTest):
    def test_analysis_search(self):
        self.geoiq.analysis.load_all_analyses()
        self.assertTrue(len(self.geoiq.analysis.algorithms) > 0)


if (__name__ == "__main__"):
    unittest.main()
