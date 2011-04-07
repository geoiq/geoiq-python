
import geoiq, jsonwrap
import urlparse, os.path
import itertools

import features

class DatasetSvc(geoiq.GeoIQSvc):
    by_id_url = "datasets/{id}.json?include_features=0"
    create_url = "datasets.json"
    update_feed_url = "datasets/{id}/fetch.json"
    features_url = "datasets/{id}/features.json?start={start}&limit={limit}&hex_geometry=1"

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

    def features(self, ds, start=0,limit = None, per_req=30):
        if limit is None:
            limit = ds.feature_count

        gen = jsonwrap.wrap_many(features.Feature.map)

        sofar = 0
        while sofar < limit:
            if (sofar + per_req) >= limit:
                per_req = limit - sofar

            u = self.url(self.__class__.features_url, start=sofar, limit=per_req, id=ds.geoiq_id)
            fin,res = self.do_req(u, "GET", None, unwrapper=gen)
            for f in fin:
                sofar+=1
                yield f



    def request_feed_update(self, ds):
        u = self.url(update_feed_url, **ds.unmap())
        r,_ = self.do_req(u, "GET", None, lambda x : x)
        return r

    def update_new(self,dataset):
        # Dataset creation is funny -- returns result as a URL in a header,
        #   body is useless (to us) HTML.
        # Override creation with one that deals w/ the w

        method = "POST"
        post = dataset.unmap()
        
        if dataset.uploads is not None: # switch to multipart & add files:
            files = dataset.uploads
            post.update(dict( ("dataset[" + k[1:] + "]", open(v,'r')) for (k,v) in files.iteritems()))
            method = "MULTIPART"

        r,f = self.raw_req(DatasetSvc.create_url, method, post)

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
    writeable = True

    FILETYPES= dict( itertools.chain( * (( (x[0],x[1:]) for x in itertools.permutations(entry) ) for entry in RAWFILETYPES  )) )

    def set_upload(self, path):
        assert(self.is_new())
        p = urlparse.urlparse(path)
        if (p.scheme == 'http' or
            p.scheme == 'https'):
            self.uploads = None
            self.link = path
            self.props['url'] = path
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

    def features(self, start=0,limit=None, per_req=30):
        return self.svc.features(self, start, limit, per_req)

jsonwrap.props(Dataset,
               "title",
               "description",
               "tags", 
               "published",
               "data_type",
               "feature_count",
               "link")
               
