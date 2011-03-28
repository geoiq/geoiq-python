import geoiq, jsonwrap, dataset #, map

class SearchSvc(geoiq.GeoIQSvc):
    name="search"

    def get_entity(self,json):
        return SearchPage

    def search(self,request,per_page=50,limit=float('inf'),bbox=None):
        # TODO: BBOX
        c = 0
        curpage = 0
        total = 1

        while (c < limit and c < total):
            o = {
                'query':request,
                'curpage':curpage,
                'limit':per_page
                }

            u = self.url("search.json?query={query}&limit={limit}&page={curpage}",o)

            fin,res = self.do_req(u, "GET", None)
            c += res['itemsPerPage']
            curpage += 1
            total = res['totalResults']
            yield fin

class SearchPointer(jsonwrap.JsonMappedObj):
    iqprops = geoiq.props("detail_link","description","type","tags",
                          "author", "id")
    def __init__(self, props, svc):
        jsonwrap.JsonMappedObj.__init__(self, props)
        self.svc = svc

    def load(self):
        pass

def search_pointers(ptrs, *args, **kwargs):
    return [SearchPointer(p,*args,**kwargs) for p in ptrs]

class SearchPage(jsonwrap.JsonMappedObj):
    iqprops = geoiq.props("totalResults",
                          entries={ "ro":True, "map_in": search_pointers })
