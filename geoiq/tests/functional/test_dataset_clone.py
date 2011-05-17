import geoiq, unittest, os.path, tempfile

from geoiq.tests.functional import *
from geoiq.tests.compare import *
from geoiq.util.protocol import obj_to_railsparams
import sys

class TestDatasetClone(GeoIQFuncTest):
    def check_cloned_datasets(self, scratch, gc_ds, fin):
        nf = os.path.join(scratch, "as_uploaded.kml")
        fin.download(nf,'kml')
        
        dc = DeepCompare()
        ok,r = dc.compare(fin.props, gc_ds.props)
        dc.pprint(r,sys.stdout,False)

        # ... features!
        orig_feats = list(p.props for p in gc_ds.features())
        n_feats = list(p.props for p in fin.features())
        
        ok, feat_diff = dc.compare(orig_feats, n_feats)
        diff_count = sum( len(r.get("diff",[])) for r in feat_diff )
        print("Feature differences: %d" % diff_count)

        if (diff_count > 0):
            report = os.path.join(scratch, "report.txt")
            repf = open(report,"w")
            dc.pprint(feat_diff,repf,False)
            repf.close()
            print("Report dumped")
    
    def test_clone_dataset(self):
        gc_ds = self.random_obj(self.geocommons.datasets).next()
        
        scratch = self.working_folder()

        dl = os.path.join(scratch, "downloaded.kml") #tempfile.NamedTemporaryFile(suffix=".kml", dir=scratch, delete=False)
        
        gc_ds.download(dl, "kml")
        
        
        cloned = self.geoiq.datasets.create(dl)
        cloned.copy_from(gc_ds)


        print(cloned.to_json_obj())

        cloned.save()
        
        fin = self.geoiq.datasets.get_by_id(cloned.geoiq_id)

        self.check_cloned_datasets(scratch, gc_ds, fin)

    def test_alter_clone(self):
        pass

if (__name__ == "__main__"):
    unittest.main()
