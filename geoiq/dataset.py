
import geoiq, util.jsonwrap as jsonwrap
import urlparse,cgi,urllib
import  os.path, tempfile, zipfile
import itertools

import features

class DatasetSvc(geoiq.GeoIQSvc):
    by_id_url = "datasets/%(id)s.json?include_features=0"
    create_url = "datasets.json"
    update_feed_url = "datasets/%(id)s/fetch.json"
    features_url = "datasets/%(id)s/features.json?start=%(start)s&limit=%(limit)s&hex_geometry=1"
    analyze_url = "datasets/%(id)s/calculate.json"

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

    def analyze(self, ds, alg, inputs):
        u = self.url(self.__class__.analyze_url, id=ds.geoiq_id)
        parms = { "algorithm": alg, "input" : inputs }
        fin,r = self.do_req(u, "POST", parms)
        return fin

    def features(self, ds, start=0,limit = None, per_req=30):
        if limit is None:
            limit = ds.feature_count

        gen = jsonwrap.map_many(features.Feature).map

        sofar = 0
        while sofar < limit:
            if (sofar + per_req) >= limit:
                per_req = limit - sofar

            u = self.url(self.__class__.features_url, start=sofar, limit=per_req, id=ds.geoiq_id)
            fin,res = self.do_req(u, "GET", None, unwrapper=gen)
            for f in fin:
                sofar+=1
                yield f

    def get_by_url(self, url):
        up = urlparse.urlparse(url)
        path = up.path
        if not up.path.endswith(".json"):
            path = up.path + ".json"
        qq = cgi.parse_qs(up.query)
        qq['include_features'] = 0
        query = urllib.urlencode(qq)
        fin_url = urlparse.urlunparse((up.scheme,
                                      up.netloc,
                                      path,
                                      up.params,
                                      query,
                                      up.fragment))
        return super(DatasetSvc,self).get_by_url(fin_url)

    def open_stream(self, ds, format="zip"):
        supported = ["zip","kml", "csv"]
        if not format in supported:
            raise ValueError("Unsupported format; must be one of [%s]" % (",".join(supported)))
        
        u = self.url("datasets/%(id)s.%(format)s", 
                     id=ds.geoiq_id,
                     format=format)
        fin, stream = self.raw_req(u, "GET", None)
        return stream

    def request_feed_update(self, ds):
        u = self.url(update_feed_url, **ds.to_json_obj())
        r,_ = self.do_req(u, "GET", None, lambda x : x)
        return r

    def update_new(self,dataset):
        # Dataset creation is funny -- returns result as a URL in a header,
        #   body is useless (to us) HTML.
        # Override creation with one that deals w/ the w

        method = "POST"
        post = dataset.to_json_obj()
        
        if dataset.uploads is not None: # switch to multipart & add files:
            post["dataset"] = dict( (k, open(v,'rb')) for (k,v) in dataset.uploads.iteritems() )
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
               [".kml"],
               [".climgen"] ]
OPTIONAL_TYPES=[ ".prj" ] # FIXME a bit of a hack

try:
    permutations_imp = itertools.permutations
except AttributeError:
    import util.backports
    permutations_imp = util.backports.permutations

class Dataset(geoiq.GeoIQObj):
    writeable = True

    FILETYPES= dict( itertools.chain( * (( (x[0],x[1:]) for x in permutations_imp(entry) ) for entry in RAWFILETYPES  )) )

    def set_upload(self, path):
        global OPTIONAL_TYPES

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
        
        fin_extensions = []
        for ext in extensions:
            if not (os.path.exists(base+ext)):
                if ext not in OPTIONAL_TYPES:
                    raise ValueError("Missing layer component: " + base + ext)
            else:
                fin_extensions.append(ext)

        self.uploads=dict( (ext[1:],base+ext) for ext in fin_extensions )
    
    def request_feed_update(self):
        service.request_feed_update(self)

    def features(self, start=0,limit=None, per_req=30):
        return self.svc.features(self, start, limit, per_req)

    def open_stream(self, format="zip"):
        return self.svc.open_stream(self, format)

    def download(self, file_or_filename, format='kml'):
        if format not in ["kml","csv","rss","zip" ]:
            raise ValueError("Unsupported format: " + format)
        
        if not hasattr(file_or_filename, "write"):
            if (os.path.exists(file_or_filename)):
                raise ValueError("File already exists: " + file_or_filename)
            if not (os.path.exists(os.path.dirname(file_or_filename))):
                raise ValueError("Directory missing: " + os.path.dirname(file_or_filename))
            outf = open(file_or_filename, "wb")
            return self.download(outf, format)

        s = self.open_stream(format)
        while True:
            dat = s.read(4096)
            if (dat == ""): break
            file_or_filename.write(dat)
        s.close()

        return file_or_filename

    def download_shapefile(self, folder, work_folder=None):
        if not os.path.isdir(folder):
            raise ValueError("Folder must exist")
        
        if work_folder is not None and not os.path.isdir(work_folder):
            raise ValueError("Work folder must exist (if given)")

        if work_folder is None:
            work_folder = tempfile.mkdtemp()

        out_path = os.path.join(work_folder, "dl%d.zip" % self.geoiq_id)
        outfile = open(out_path, "wb")

        self.download(outfile, format="zip")

        outfile.close()
        
        if not zipfile.is_zipfile(out_path):
            raise ValueError("Download failed or corruption?")
        
        zipf = zipfile.ZipFile(out_path)
        try:
            extractor = zipfile.ZipFile.extractall
        except AttributeError:
            extractor = util.backports.zip_extract_all

        extractor(zipf,folder)

        nms = [ os.path.abspath(os.path.join(folder,nm)) 
                for nm in zipf.namelist() ]
        
        shp = None
        for nm in nms:
            if (nm.lower().endswith(".shp")):
                shp = nm
            assert(os.path.exists(nm))

        zipf.close()

        return (shp,nms)

    def analyze(self, alg, inps):
        return self.svc.analyze(self, alg, inps)

jsonwrap.props(Dataset,
               "title",
               "description",
               "tags", 
               "published",
               "data_type",
               "feature_count",
               "author",
               "source",
               link={"ro":True},
               contributor={"ro":True},
               published={"ro":True})
               
