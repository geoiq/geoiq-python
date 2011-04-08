import geoiq, util.jsonwrap as jsonwrap, dataset
try: import simplejson as json
except ImportError: import json

class MapSvc(geoiq.GeoIQSvc):
    create_url = "maps.json"
    by_id_url = "maps/{id}.json"

    def get_entity(self,json):
        return Map

geoiq.GeoIQ.regsvc("maps", MapSvc)

class Map(geoiq.GeoIQObj):
    writeable = True

    # def unmap(self):
    #     # Unwrapping a map into post args is
    #     #  complex enough to just need to be done manually:
    #     p = geoiq.GeoIQObj.unmap(self) # starting point

    #     fin = {}
    #     for x in ["id",
    #               "title",
    #               "basemap",
    #               "description"]:
    #         fin[x] = p.get(x)

        

    #     # flatten tags:
    #     # fin["tags"] = ",".join(p.get("tags",[]))

    #     # Permissions... ??
    #     # fin["permissions"] = json.dumps(p.get("permissions",{}))

    #     return fin
        

jsonwrap.props(Map, 
               "title",
               "basemap",
               "description",
               "tags",
               "extent",
               "projection",
               "permissions",
               "layers")     

