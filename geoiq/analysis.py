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

        flatargs = {
            "calculation" : algorithm
            }
        flatargs.update(inputs)
        

        r,f = self.do_req(self.getapi("analysis_go_url"), "POST", flatargs, unwrapper=geoiq.ident)


        # Success =  redirect!
        fin_id = r["id"]

        return self.geoiq.datasets.get_by_id(fin_id)

    def add_analysis_algorithm(self, a):
        
        # Wrap a parsed analysis description into something that boils
        #  into a call to .analyze()
        assert(a.built_in and a.formula is None), "Can only add builtin algorithms"

        assert(not hasattr(self, "analyze_" + a.algorithm)),("already have %s algorithm defined" % a.algorithm)

        def dotype(t,v):
            if isinstance(t, str):
                # type names: .. "attribute", "dataset","dataset_input", "boundary", 
                # TODO: collect all known type names? 
                if (hasattr(v, 'state')):
                    if (v.state != 'complete'):
                        # TODO: once the API returns correct state values:
                        # raise ValueError("Can't analyize an incomplete dataset.")
                        return v.geoiq_id
                    else:
                        return v.geoiq_id

            if hasattr(t, "__len__"):
                # array -- 'tis like an enum.
                pass
            elif hasattr(t,"__getitem__"):
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
        self.algorithms.append((a.algorithm, res_method, a))

    def load_all_analyses(self):
        a = self.geoiq.search("",model=Analysis)
        for searchres in a:
            assert(searchres.is_analysis()), ("Searching for analysis returned results of type %s instead." % searchres.tp)  # (Permissions?) we sometimes get datasets and maps back.
            res = searchres.load()
            if res.built_in and (res.formula is None):
                self.add_analysis_algorithm(res)

geoiq.GeoIQ.regsvc("analysis", AnalysisSvc)

class Analysis(geoiq.GeoIQObj):
    @classmethod
    def is_ro(cls): return True



jsonwrap.props(Analysis, 
               "built_in", "algorithm","formula", "instruction", "parameters")
