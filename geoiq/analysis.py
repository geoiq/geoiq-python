import geoiq, util.jsonwrap as jsonwrap
import urlparse

class AnalysisSvc(geoiq.GeoIQSvc):
    by_id_url = "analysis_by_id_url"

    def __init__(self,*args, **kargs):
        self.algorithms = []
        geoiq.GeoIQSvc.__init__(self,*args,**kargs)

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
        

        r,f = self.raw_req("analysis_go_url", "POST", args)

        print("Finished!")
        tmplog = open("scratch/analysis.txt", "w")
        tmplog.write(r.read())
        tmplog.close()


        # Success =  redirect!
        fin_loc = r.geturl()

        assert(fin_loc is not None), "Didn't get a location back from the server"
        fin_id = urlparse.urlparse(fin_loc).path.split("/")[-2]
        
        return self.geoiq.datasets.get_by_id(fin_id)

    def add_analysis_algorithm(self, a):
        
        # Wrap a parsed analysis description into something that boils
        #  into a call to .analyze()
        assert(a.built_in and a.formula is None), "Can only add builtin algorithms"

        assert(not hasattr(self, "analyze_" + a.algorithm)),("already have %s algorithm defined" % a.algorithm)

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

        def res_method(**kargs):
            args = dict(p(kargs) for p in parsers)
            return self.analyze(a.algorithm, args)

        res_method.__doc__ = a.instruction
        
        setattr(self, "analyze_" + a.algorithm, res_method)
        self.algorithms.append((a.algorithm, res_method))

    def load_all_analyses(self):
        a = self.geoiq.search("",model=Analysis)
        for searchres in a:
            assert(searchres.is_analysis()), ("Searching for analysis returned results of type %s instead." % searchres.tp)  # (Permissions?) we sometimes get datasets and maps back.
            res = searchres.load()
            if res.built_in and (res.formula is None):
                self.add_analysis_algorithm(res)

geoiq.GeoIQ.regsvc("analysis", AnalysisSvc)

class Analysis(jsonwrap.JsonWrappedObj):
    pass

jsonwrap.props(Analysis, 
               "built_in", "algorithm","formula", "instruction", "parameters")
