import geoiq, jsonwrap, dataset
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

    def unmap(self):
        # Unwrapping a map into post args is
        #  complex enough to just need to be done manually:
        p = geoiq.GeoIQObj.unmap(self) # starting point

        fin = {}
        for x in ["id",
                  "title",
                  "basemap",
                  "description"]:
            fin[x] = p.get(x)

        # build the layers array
        #  1) only included on create.
        #  2) layer properties flattened out completely
        #  NOTE: not sure about the encoding below...
        #    arrays are with [] after the name, dict members with a keyword
        #    in them?

        # curl -i -u "user:password" -d "layers[][source]=finder:92674" -d "title=Vehicles by Ward" -d "[layers][][styles][fill][classificationType]=St Deviation" -d "layers[][styles][fill][categories]=5" -d "layers[][styles][fill][colors][]=15725567" -d "layers[][styles][fill][colors][]=12441575" -d "layers[][styles][fill][colors][]=7057110" -d "layers[][styles][fill][colors][]=3244733" -d "layers[][styles][fill][colors][]=545180" -d "basemap=Google Terrain" -d "title=Abandoned Vehicle Requests by Ward DC" -d "layers[][styles][fill][selectedAttribute]=overdue request count" -d "layers[][styles][type]=CHOROPLETH"  -d "extent[]=-77" -d "extent[]=38" -d "extent[]=-76" -d "extent[]=39" -X POST http://geocommons.com/maps.json

        l = p.get("layers",[])
        for idx in range(len(l)):
            for (k,v) in l[idx].iteritems():
                nm = "layers[%d][%s]" % (idx,k)
                if ("styles" == k):
                    v = json.dumps(v) # TODO: Is this right?
                fin[nm] = v

        # flatten tags:
        fin["tags"] = ",".join(p.get("tags",[]))

        # Permissions... ??
        fin["permissions"] = json.dumps(p.get("permissions",{}))

        return fin
        

jsonwrap.props(Map, 
               "title",
               "basemap",
               "description",
               "tags",
               "extent",
               "projection",
               "permissions",
               "layers")     

