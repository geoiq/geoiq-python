import unittest
from geoiq.tests.functional import *


class TestAnalysis(GeoIQFuncTest):
    def test_analysis_search(self):
        self.geoiq.analysis.load_all_analyses()
        self.assertTrue(len(self.geoiq.analysis.algorithms) > 0)


    def test_analysis_methods(self):
        self.geoiq.analysis.load_all_analyses()

        tests = self.conf.get("test_analysis", [])
        for test in tests:
            mtd = getattr(self.geoiq.analysis, test["algorithm"])
            t = dict(test)
            del t["algorithm"]
            res = mtd(**t)
            self.assertTrue(res is not None)
            print("Output Analysis title: %s" % res.title)

if (__name__ == "__main__"):
    unittest.main()
