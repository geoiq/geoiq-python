
import geoiq, jsonwrap
import urlparse, os.path
import itertools
class DatasetSvc(geoiq.GeoIQSvc):
    by_id_url = "datasets/{id}.json?include_features=0"
    create_url = "datasets.json"
    update_feed_url = "datasets/{id}/fetch.json"
    
    def get_entity(self,json):
        return Dataset

    def create(self, path_or_url):
        """\
        Create a new (unsaved) dataset.
        
        path_or_url -- A path to a file to upload, or a URL to a feed
           to pull from. If the file is one component of a shapefile,
           the others (.prj, .dbf, .shx) will also be uploaded.

        """

        ds = Dataset(None, self)
        ds.set_upload(path_or_url)
        return ds


    def request_feed_update(self, ds):
        u = self.url(update_feed_url, ds)
        r,_ = self.do_req(u, "GET", None, lambda x : x)
        return r
    
    def update(self, ds):
        if (ds.is_new()):
            return self.upload(ds, ds.uploads)
        else:
            return geoiq.GeoIQSvc.update(self,ds)

    def upload(self, dataset, files):
        post = dict( ("dataset[" + k[1:] + "]", open(v,'r')) for (k,v) in files.iteritems())
        post.update(dataset.props)

        # Do the request with no parsing/unwrapping -- the result is
        #  a big html/xml page; but there's a pointer to the final JSON
        #  in the 'location' header coming back from the server.
        def nop(x): return x

        r,f = self.do_req(DatasetSvc.create_url, "MULTIPART",post, 
                          unwrapper=nop, parser=nop)
        
        fin_loc = r.info()["location"]

        assert(fin_loc is not None), "Didn't get a location back from server on multipart/post?"
        assert(fin_loc != ""), "Didn't get a location back from server on multipart/post?"

        f.close()
        
        fin_filename = urlparse.urlparse(fin_loc).path.split("/")[-1]
        fin_id = fin_filename[:-(len(".json"))]
        assert(fin_filename[-len(".json"):] == ".json")

        # Force refresh:
        dataset.props["id"] = fin_id
        dataset.refresh(True)

        return dataset

geoiq.GeoIQ.regsvc("datasets", DatasetSvc)

RAWFILETYPES=[ [".shp",".dbf",".shx",".prj"],
               [".csv"],
               [".rss"],
               [".kmz"],
               [".climgen"] ]


class Dataset(geoiq.GeoIQObj):
    FILETYPES= dict( itertools.chain( * (( (x[0],x[1:]) for x in itertools.permutations(entry) ) for entry in RAWFILETYPES  )) )

    def set_upload(self, path):
        assert(self.is_new())
        p = urlparse.urlparse(path)
        if (p.scheme == 'http' or
            p.scheme == 'https'):
            self.uploads = None
            self.link = path
            return

        if not (os.path.exists(path)): raise ValueError("File must exist: " + path)

        base,ext = os.path.splitext(path)
        ext = ext.lower()
        more = Dataset.FILETYPES.get(ext)
        if not (more is not None): raise ValueError("Unsupported filetype")
        extensions = [ext] + list(more)
        
        # TODO: technically, the .prj shouldn't be mandatory
        for ext in extensions:
            if not (os.path.exists(base+ext)):
                raise ValueError("Missing layer component: " + base + ext)

        self.uploads=dict( (ext,base+ext) for ext in extensions )
    
    def request_feed_update(self):
        service.request_feed_update(self)

jsonwrap.props(Dataset,
               "title",
               "description",
               "tags",
               "published",
               "data_type",
               "feature_count",
               "link")
               
