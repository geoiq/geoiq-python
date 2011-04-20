import geoiq, util.jsonwrap as jsonwrap, dataset
try: import simplejson as json
except ImportError: import json

class MapSvc(geoiq.GeoIQSvc):
    create_url = "maps.json"
    by_id_url = "maps/%(id)s.json"
    layer_add_url = "maps/%(id)s/layers.json"

    def get_entity(self,json):
        return Map

    def map_add_layer(self, m, lyr):
        if (m.is_new()): raise ValueError("Can't add layers to an unsaved map.")
        u = self.url(self.__class__.layer_add_url, id=m.geoiq_id)
        ra,rb = self.raw_req(u, "POST", lyr.to_json_obj())
        

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
               "type",
               "visible",
               "layer_id",
               "subtitle",
               "opacity",
               "styles",
               source={"map":LayerSource})

# The map!
class Map(geoiq.GeoIQObj):
    writeable = True
    
    def add_layer(self, source):
        if self.layers is None: self.layers = []
        if not isinstance(source, LayerSource):
            source = LayerSource(source, self.geoiq)

        res = Layer({"source":source})
        
        fin = self.svc.map_add_layer(self, res)
        self.refresh()

        for l in self.layers:
            if (l.source.dataset_id == source.dataset_id):
                return l
        raise ValueError("Couldn't find the saved layer?")



jsonwrap.props(Map, 
               "title",
               "basemap",
               "description",
               "tags",
               "extent",
               "projection",
               "permissions", # TODO: map to permissions
               layers={"map":jsonwrap.map_many(Layer)},
               contributor={"ro":True})

