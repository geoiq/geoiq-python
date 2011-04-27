import geoiq, util.jsonwrap as jsonwrap
import urlparse

class AnalysisSvc(geoiq.GeoIQSvc):
    refine_url = "refiners"
    by_id_url = "refinements/%(id)s.json"

    def update(self, *args):
        raise ValueError("Read-only for now.")
    
    def get_entity(self, json):
        return Analysis

    def analyze(self, algorithm, inputs):
        # use refiner:
        args = {
            "[refiner]": {
                "parameters" : {
                    "calculation" : algorithm,
                    "input" : inputs
                    }
                }
            }
        

        r,f = self.raw_req(AnalysisSvc.refine_url, "POST", args)

        # Success =  redirect!
        fin_loc = r.geturl()

        assert(fin_loc is not None), "Didn't get a location back from the server"
        fin_id = urlparse.urlparse(fin_loc).path.split("/")[-2]
        
        return self.geoiq.datasets.get_by_id(fin_id)

    def add_analysis_algorithm(self, a):
        # Wrap a parsed analysis description into something that boils
        #  into a call to .analyze()
        assert(a.built_in and a.formula is None), "Can only add builtin algorithms"

        assert(not hasattr(self, "analyze_" + a.algorithm)),"already have this algorithm defined"

        def dotype(t,v):
            if isinstance(v, str):
                # type names: .. "attribute", "dataset", "boundary", 
                # TODO: collect all known type names
                pass
            if hasattr(v, "__len__"):
                # array -- 'tis like an enum.
                pass
            elif hasattr(v,"__getitem__"):
                # dict
                pass
            return v
                

        def pp(d): # parse a param
            def res(kargs):
                v = dotype(d['type'], kargs.get(d['id']))
                
                if (d.get('required') and v is None):
                    raise ValueError("Missing required parameter %s" % d['id'])
                return (d['id'],v)
            return res
        
        parsers = [ pp(param) for param in a.parameters ]

        def res_method(self, **kargs):
            args = dict(p(kargs) for p in parsers)
            return self.analyze(a.algorithm, args)

        res_method.__doc__ = a.instruction
        
        setattr(self.__class__, "analyze_" + a.algorithm, res_method)
                

    def load_all_analyses(self):
        a = [ r.load() for r in self.geoiq.search("",model=Analysis) ]
        for res in a:
            if res.built_in and (res.formula is None):
                self.add_analysis_algorithm(res)

geoiq.GeoIQ.regsvc("analysis", AnalysisSvc)

class Analysis(jsonwrap.JsonWrappedObj):
    pass

jsonwrap.props(Analysis, 
               "built_in", "algorithm","formula", "instruction", "parameters")
