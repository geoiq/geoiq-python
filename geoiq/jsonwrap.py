
# Internal utility classes to make mapping to/from JSON web services easier


class JsonWrappedObj(object):
    """
    Base for objects mapped in from JSON.
    """
    def __init__(self, props, *args):
        self.props = props
        self.isdirty = False

    def dirty(self):
        return self.isdirty

    def copy_from(self, other):
        """ Shallow copy writeable properties across from the other object """
        for pname in other.__class__.mappings:
            if  not self.mappings.get(pname,{}).get('ro',True):
                if pname in other.props: self.props[pname] = other.props[pname]
        return self

    @classmethod
    def map(cls,json, *args, **kwargs):
        """
        Constructs an object from JSON, applying mappings along the way.
        """
        mapping = cls.mappings
        
        def id(x,*args, **kwargs): return x

        njson = dict(
            (k,mapping.get(k,{}).get('in', id)(v, *args,**kwargs))
            for (k,v) in json.iteritems()
            )

        return cls(njson, *args, **kwargs)

    def unmap(self, *args, **kwargs):
        """
        Converts this to a bare dict for JSON, applying mappings along the way
        """
        mapping = self.__class__.mappings
        def id(x,*args,**kargs):return x
        return dict(
            (k, mapping.get(k,{}).get('out', id)(v, *args, **kwargs))
            for (k,v) in self.props.iteritems()
            )

    @classmethod
    def is_readonly(cls):
        return not getattr(cls,"writeable",False)

def wrap_many(inner):
    def r(ps, *args, **kargs):
        return [ inner(p,*args,**kargs) for p in ps ]
    return r

def props(cls, *simple,**specs):
    """\
    Define properties mapped to the underlying json.
    
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
        
    ro_def = cls.is_readonly()

    # Make sure there's a class-level mapping dictionary:
    setattr(cls, "mappings", getattr(cls,"mappings", {}))

    for p in simple:
        doprop(p, ro_def, p)
        cls.mappings[p] = { "ro" : ro_def }
    for (nm,attrs) in specs.iteritems():
        doprop(nm, 
               ro_def or attrs.get('ro', False), 
               attrs.get('mapto', nm))
        cls.mappings[nm] = { "ro" : ro_def or attrs.get('ro',False) }
        if "map_in" in attrs:
            cls.mappings[nm]["in"] = attrs["map_in"]
        if "map_out" in attrs:
            cls.mappings[nm]["out"] = attrs["map_out"]

