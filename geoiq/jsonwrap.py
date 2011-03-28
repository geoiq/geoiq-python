
# Internal utility classes to make mapping to/from JSON web services easier

class __StaticBase(object):
    @classmethod
    def _cls_init(cls, *a, **kwas):
        return

def props(*p,**ps):
    @classmethod
    def r(cls):
        cls._iqprops(*p,**ps)
    return r

class JsonMappedObj(__StaticBase):
    """
    Base for objects mapped in from JSON.
    """
    def __init__(self, props, *args):
        self._cls_init()
        self.props = props
        self.isdirty = False

    def dirty(self):
        return self.isdirty

    @classmethod
    def map(cls,json, *args, **kwargs):
        cls._cls_init()


        mapping = cls.mappings
        
        def id(x,*args, **kwargs): return x

        njson = dict(
            (k,mapping.get('in_' + k, id)(*([v]+list(args)),**kwargs))
            for (k,v) in json.iteritems()
            )

        return cls(njson, *args, **kwargs)

    @classmethod
    def is_ro(cls): return True

    @classmethod
    def _cls_init(cls, inSuper = False):
        """ Hacky hacky static initialization. """
        if (hasattr(cls, '__cls_inited') ):
            return

        if not inSuper:
            setattr(cls, "__cls_inited", True)
        
        cls.__mro__[1]._cls_init(True)

        cls.iqprops()

    iqprops = props()
    @classmethod
    def _iqprops(cls, *simple,**specs):
        """\
        Define properties mapped to the GeoIQ service backend.
        
        Side effect: Add the 'right' default constructor if it's needed.

        Normal arguments get a simple read/write property.
        Keyword arguments: { ro:True, map_in:in_map_fn, map_out:out_map_fn}
          (all optional)
        """

        # bit of metaprogramming .. 
        def mkprop(name, ro):

            # Cribbing a bit from
            #  http://code.activestate.com/recipes/157768/
            def rd(self):
                return self.props.get(name)
            if (ro):
                return property(rd)
            def wr(self,v):
                if v == self.props.get(name):
                    return v
                
                self.props[name] = v
                self.isdirty = True

                return v
            return property(rd,wr)   

        def doprop(nm, ro, mapto):
            setattr(cls,nm, mkprop(mapto,ro))
            
        ro_def = cls.is_ro()

        # Make sure there's a class-level mapping dictionary:
        setattr(cls, "mappings", getattr(cls,"mappings", {}))

        for p in simple:
            doprop(p, False, p)
        
        for (nm,attrs) in specs.iteritems():
            doprop(nm, 
                   ro_def or attrs.get('ro', False), 
                   attrs.get('mapto', nm))

            if "map_in" in attrs:
                cls.mappings["in_" + nm] = attrs["map_in"]
            if "map_out" in attrs:
                cls.mappings["out_" + nm] = attrs["map_out"]
                

    

