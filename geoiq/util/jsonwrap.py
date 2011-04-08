
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

    def to_json_obj(self):
        return self.__class__.unmap(self)
    
    @classmethod
    def map(cls,json, *args, **kwargs):
        """
        Constructs an object from JSON, applying mappings along the way.
        """
        mapping = cls.mappings
        
        def map_in(mapper,v):
            if mapper is None: return v
            else: return mapper.map(v, *args, **kwargs)
        
        njson = dict(
            (k,map_in(mapping.get(k,{}).get('mapper'), v))
            for (k,v) in json.iteritems()
            )

        return cls(njson, *args, **kwargs)

    @classmethod
    def unmap(cls, obj, *args, **kwargs):
        """
        Converts this to a bare dict for JSON, applying mappings along the way.
        Only explicitly-defined props are unmapped.
        """
        mapping = cls.mappings

        def map_out(mapper,v):
            if mapper is None: return v
            else: return mapper.unmap(v, *args, **kwargs)

        itms = ( (k,v) for (k,v) in obj.props.iteritems() if k in mapping )

        return dict(
            (k,map_out(mapping[k].get('mapper'),v))
            for (k,v) in itms
            )

    @classmethod
    def is_readonly(cls):
        return not getattr(cls,"writeable",False)

class map_many(object):
    def __init__(self, inner):
        self.inner = inner

    def map(self,ps, *args, **kargs):
        return [ self.inner.map(p,*args,**kargs) for p in ps ]
    
    def unmap(self,ps, *args, **kargs):
        return [ self.inner.unmap(p, *ags, **kargs) for p in ps ]

def props(cls, *simple,**specs):
    """\
    Define properties mapped to the underlying json.
    
    Normal arguments get a simple read/write property.
    Keyword arguments: { ro:True, map:<object with .map and .unmap attrs> }
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
        if "map" in attrs:
            cls.mappings[nm]["mapper"] = attrs["map"]
