import geoiq, jsonwrap, dataset #, map

class SearchSvc(geoiq.GeoIQSvc):
    name="search"

    def get_entity(self,json):
        return SearchPage

    def search(self,request,per_page=50,page_limit=float('inf'),bbox=None):
        # TODO: BBOX
        c = 0
        curpage = 0
        total = 1

        while (curpage < page_limit and c < total):
            o = {
                'query':request,
                'curpage':curpage,
                'limit':per_page
                }

            u = self.url("search.json?query={query}&limit={limit}&page={curpage}",**o)

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

    def load(self):
        tp,key = self.id.split(":")
        
        loader = {
            "Dataset":self.geoiq.datasets.get_by_id,
            "Map":None,
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
