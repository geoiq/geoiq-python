import geoiq, unittest

from geoiq.tests.functional import *
from geoiq.tests.compare import *

class TestDatasetClone(GeoIQFuncTest):
    def test_clone_dataset(self):
        gc_ds = self.random_obj(self.geocommons.datasets).next()
        
        scratch = self.working_folder()

        fin,others = gc_ds.download_shapefile(scratch, work_folder=scratch)
        
        cloned = self.geoiq.datasets.create(fin)
        cloned.copy_from(gc_ds)
        cloned.save()
        
        fin = self.geoiq.datasets.get_by_id(cloned.geoiq_id)
        
        dc = DeepCompare()
        ok,r = dc.compare(fin.props, gc_ds.props)
        dc.pprint(r)

        # ... features!
        orig_feats = list(gc_ds.features())
        n_feats = list(fin.features())
        
        ok, feat_diff = dc.compare(orig_feats, n_feats)
        diff_count = sum( len(r.get("diff",[])) for r in feat_diff )
        print("Feature differences: %d" % diff_count)

        if (diff_count > 0):
            ndir = os.path.join(scratch, "as_uploaded")
            os.mkdir(ndir)
            fin.download_shapefile(ndir)
            report = os.path.join(scratch, "report.txt")
            repf = open(report,"w")
            dc.pprint(feat_diff,False, repf)
            repf.close()
            print("Report dumped")

if (__name__ == "__main__"):
    unittest.main()
