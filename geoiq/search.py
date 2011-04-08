import geoiq, util.jsonwrap as jsonwrap, dataset, map

class SearchSvc(geoiq.GeoIQSvc):
    name="search"

    def get_entity(self,json):
        return SearchPage

    def search(self,request,
               start_page=0,
               per_page=50,
               model=None,
               page_limit=float('inf'),
               bbox=None):
        if model is not None:
            def might_be(x, *xs):
                for xx in xs:
                    try: 
                        if (x is xx or isinstance(x,xx) ): return True
                    except TypeError: pass
                return False

            if (might_be(model, dataset, dataset.Dataset, dataset.DatasetSvc)):
                model = "Overlay"
            elif (might_be(model, map, map.Map, map.MapSvc)):
                model = "Map"
        
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

            u = self.url("search.json", query=o)
            print("Search url:" + u)
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

    def load(self):
        loader = {
            "Dataset":self.geoiq.datasets.get_by_id,
            "Map":self.geoiq.maps.get_by_id,
            "Overlay":self.geoiq.datasets.get_by_id
            }.get(self.tp)
        
        if (loader is None):
            raise NotImplementedError("No implementation for: " + tp + "yet.")
        
        return loader(self.key)


jsonwrap.props(SearchPointer,
               "detail_link",
               "description",
               "type",
               "tags",
               "author", 
               "id")


def search_pointers(ptrs, *args, **kwargs):
    return [SearchPointer(p,*args,**kwargs) for p in ptrs]

class SearchPage(jsonwrap.JsonWrappedObj):
    pass

jsonwrap.props(SearchPage,
               "totalResults",
               "itemsPerPage",
               entries={ "ro":True, 
                         "map": jsonwrap.map_many(SearchPointer) })
