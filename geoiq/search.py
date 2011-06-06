import geoiq, util.jsonwrap as jsonwrap, dataset, map, analysis

class SearchSvc(geoiq.GeoIQSvc):
    name="search"

    def get_entity(self,json):
        return SearchPage

    def by_username(self, username, *args, **kargs):
        return self.search("user:%s" % username, *args, **kargs)

    def search(self, request, model=None, bbox=None, max_results=None):
        per_page = 50
        page_limit = None
        if (max_results is not None):
            page_limit = (max_results / per_page) + 1

        totcount = 0
        done = False

        for page in self.search_raw(request, per_page=per_page,
                                 model=model,
                                 page_limit = page_limit,
                                 bbox = bbox):
            
            for r in page.entries:
                if max_results is not None and (totcount  >= max_results):
                    done=True
                    break

                yield r
                totcount += 1

            if done:
                break
 

    def datasets(self, request, bbox=None, max_results=None):
        return self.search(request, dataset.Dataset, bbox, max_results)

    def maps(self, request, bbox=None, max_results=None):
        return self.search(request, map.Map, bbox, max_results)

    def search_raw(self,request,
               start_page=0,
               per_page=50,
               model=None,
               page_limit=None,
               bbox=None):
        if page_limit is None: page_limit = float('inf')
        if model is not None:
            if model == "map": model = map.Map
            elif model == "dataset": model = dataset.Dataset
            elif model == "analysis": model= analysis.Analysis
            def might_be(x, *xs):
                for xx in xs:
                    try: 
                        if (x is xx or isinstance(x,xx) ): return True
                    except TypeError: pass
                return False

            if (might_be(model, dataset, dataset.Dataset, dataset.DatasetSvc)):
                model = self.getapi("search_dataset_name")
            elif (might_be(model, map, map.Map, map.MapSvc)):
                model = self.getapi("search_map_name")
            elif (might_be(model, analysis, analysis.Analysis, analysis.AnalysisSvc)):
                model = self.getapi("search_analysis_name")
        
        if self.getapi("search_analysis_name") == model and self.geoiq.endpoint.username is None:
            raise ValueError("Search for analyses only works when logged in.")

        if bbox is not None:
            bbox = ",".join( ("%f" % x) for x in bbox )

        c = 0
        curpage = start_page
        total = 1
        fin_page = start_page + page_limit
        while (curpage < fin_page and c < total):
            o = {
                'query':request,
                'page':curpage,
                'limit':per_page,
                'model': model,
                'bbox' : bbox
                }

            u = self.url("search", query=o)
            fin,res = self.do_req(u, "GET", None)
            c += fin.itemsPerPage
            curpage += 1
            total = fin.totalResults
            yield fin

    def __call__(self, *args, **kwargs):
        return self.search(*args,**kwargs)

geoiq.GeoIQ.regsvc("search", SearchSvc)

class SearchPointer(jsonwrap.JsonWrappedObj):

    def __init__(self, props, svc):
        jsonwrap.JsonWrappedObj.__init__(self, props)
        self.svc = svc
        self.geoiq = svc.geoiq

        self.tp,self.key = self.id.split(":")
        self.key = int(self.key)

    # TODO: what kind is it?
    def is_dataset(self):
        return self.tp == self.svc.getapi("search_dataset_name")

    def is_map(self):
        return self.tp == self.svc.getapi("search_map_name")

    def is_analysis(self):
        return self.tp == self.svc.getapi("search_analysis_name")

    def load(self):
        loader = None
        if self.is_dataset():
            loader = self.geoiq.datasets.get_by_id
        elif self.is_map():
            loader = self.geoiq.maps.get_by_id
        elif self.is_analysis():
            loader = self.geoiq.analysis.get_by_id

        if (loader is None):
            raise NotImplementedError("No implementation for: " + tp + "yet.")
        
        return loader(self.key)


jsonwrap.props(SearchPointer,
               "detail_link",
               "description",
               "type",
               "tags",
               "author",
               "title",
               "id")


def search_pointers(ptrs, *args, **kwargs):
    return [SearchPointer(p,*args,**kwargs) for p in ptrs]

class SearchPage(jsonwrap.JsonWrappedObj):
    pass

jsonwrap.props(SearchPage,
               "totalResults",
               "itemsPerPage",
               "next",
               entries={ "ro":True, 
                         "map": jsonwrap.map_many(SearchPointer) })
