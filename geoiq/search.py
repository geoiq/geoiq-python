import geoiq, jsonwrap, dataset, map

class SearchSvc(geoiq.GeoIQSvc):
    name="search"

    def get_entity(self,json):
        return SearchPage

    def search(self,request,per_page=50,model=None,page_limit=float('inf'),bbox=None):
        if model is not None:
            def might_be(x, *xs):
                for xx in xs:
                    if (isinstance(x,xx) or x is xx): return True
                return False

            if (might_be(model, dataset, dataset.Dataset, dataset.DatasetSvc)):
                model = "Overlay"
            elif (might_be(model, map, map.Map, map.MapSvc)):
                model = "Map"
        
        if bbox is not None:
            bbox = ",".join( ("%f" % x) for x in bbox )

        c = 0
        curpage = 0
        total = 1

        while (curpage < page_limit and c < total):
            o = {
                'query':request,
                'curpage':curpage,
                'limit':per_page,
                'model': model,
                'bbox' : bbox
                }

            u = self.url("search.json", query=o)

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
        self.tp = self.id.split(":")[0]

    def load(self):
        tp,key = self.id.split(":")
        
        loader = {
            "Dataset":self.geoiq.datasets.get_by_id,
            "Map":self.geoiq.maps.get_by_id,
            "Overlay":self.geoiq.datasets.get_by_id
            }.get(tp)
        
        if (loader is None):
            raise NotImplementedError("No implementation for: " + tp + "yet.")
        
        return loader(key)


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
                         "map_in": jsonwrap.wrap_many(SearchPointer) })
