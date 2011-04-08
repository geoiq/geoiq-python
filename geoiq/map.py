import geoiq, util.jsonwrap as jsonwrap, dataset
try: import simplejson as json
except ImportError: import json

class MapSvc(geoiq.GeoIQSvc):
    create_url = "maps.json"
    by_id_url = "maps/{id}.json"

    def get_entity(self,json):
        return Map

geoiq.GeoIQ.regsvc("maps", MapSvc)

# preliminaries -- a pointer to a layer:
class LayerSource(object):
    def __init__(self, v, gq):
        self.geoiq = gq
        if (hasattr(v,"geoiq_id")):
            self.dataset_id = v.geoiq_id
        else: self.dataset_id = v
            
    @classmethod
    def map(cls, v, svc, *args, **kwargs):
        if (isinstance(v,str)):
            vs = v.split(":")
            if (len(vs) != 2): return v
            a,b = vs
            if (a != "finder"): 
                return v
            return LayerSource(int(b), svc.geoiq)
        else:
            return v
        
    @classmethod
    def unmap(cls, v, *args, **kwargs):
        if (isinstance(v,LayerSource)):
            return "finder:%d" % v.dataset_id
        else:
            return v

    def load_dataset(self):
        return self.geoiq.datasets.get_by_id(self.dataset_id)

# Layers themselves:
class Layer(jsonwrap.JsonWrappedObj):
    writeable=True
    
    def load_dataset(self):
        return self.source.load_dataset()

    def remove(self):
        self.__removed = True

    @classmethod
    def unmap(c,s,*args,**kargs):
        if hasattr(s, "__removed"): 
            return None
        else: 
            r = super(Layer,c).unmap(s,*args,**kargs)
            return r

jsonwrap.props(Layer,
               "title",
               "subtitle",
               "opacity",
               "styles",
               source={"map":LayerSource})

# The map!
class Map(geoiq.GeoIQObj):
    writeable = True
    
    # TODO: not using the create-layer endpoint .. is that ok?
    def new_layer(self, source, position=None):
        if self.layers is None: self.layers = []
        if not isinstance(source, LayerSource):
            source = LayerSource(source, self.geoiq)

        res = Layer({"source":source})
        if position is not None: self.layers.insert(position, res)
        else: self.layers.append(res)
        return res
    

jsonwrap.props(Map, 
               "title",
               "basemap",
               "description",
               "tags",
               "extent",
               "projection",
               "permissions", # TODO: map to permissions
               layers={"map":jsonwrap.map_many(Layer)})

