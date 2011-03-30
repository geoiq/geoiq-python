import geoiq
import geoiq.dataset
import unittest as ut
import tempfile, os, os.path

class TestDataset(ut.TestCase):
    def test_upload_files(self):
        g = geoiq.GeoIQ()
        def failer(name):
            def r():
                ds = g.datasets.create(name)
                return ds
            return r

        self.assertRaises(ValueError,failer("some_path_/erhoinowwh"))

        # we know this module's file exists, but it's a .py or .pyc:
        self.assertRaises(ValueError,failer(__file__)) 
        
        # .csv works on its own
        tmpf = tempfile.NamedTemporaryFile(suffix=".csv")
        ds = g.datasets.create(tmpf.name)
        self.assertTrue(isinstance(ds, geoiq.dataset.Dataset))
        tmpf.close()

        # .shp fails on its own
        tmpf = tempfile.NamedTemporaryFile(suffix=".shp")
        self.assertRaises(ValueError, failer(tmpf.name))
        tmpf.close()
        
        # .. but, with friends, it works.
        tdir = tempfile.mkdtemp()
        xs = [ '.shp', '.shx', '.prj', '.dbf' ]
        files = [ os.path.join(tdir,"file" + x) for x in xs ]

        handles = [ open(f, "w") for f in files ]

        # (doesn't matter which file we point it at; it should find them all)
        dats = [ g.datasets.create(f) for f in files ]

        for d in dats: 
            self.assertTrue(isinstance(d,geoiq.dataset.Dataset))
            for i in range(len(xs)): 
                self.assertTrue(d.uploads.has_key(xs[i]))
                self.assertEquals(d.uploads[xs[i]], files[i]) 
        
        # cleanup
        for h in handles : h.close()
        for f in files : os.remove(f)
        os.rmdir(tdir)
        
             
        
        
