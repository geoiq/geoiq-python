import shapely.geometry as geom
import shapely.geometry.collection as geom_col
import features

class Factory(object):
    def point(self,kind,x,y):
        if ("point" == kind):
            return geom.Point(x,y)
        else:
            return (x,y)
        
    def linestring(self,kind,points):
        if ("linestring" == kind):
            return geom.LineString(list(points))
        else:
            return list(points)

    def polygon(self,kind,parts):
        if ("polygon" == kind):
            p = [ list(p) for p in parts ]
            hd = p[0]
            rst = p[1:]
            return geom.Polygon(list(hd),list(rst))
        else:
            return list(parts) 
                
                
    def multi(self,kind, sub_geoms):
        s = {
            "multipoint":geom.MultiPoint,
            "multilinestring":geom.MultiLineString,
            "multipolygon":geom.MultiPolygon,
            "geometrycollection":geom_col.GeometryCollection
            }.get(kind)
        if s is None:
            raise ArgumentError("Shapely does not support:" + kind)
        
        return s(list(sub_geoms))

shapely_factory = Factory()
def to_shapely(self):
    global shapely_factory
    return (self.attributes(), self.raw_parse(shapely_factory))

setattr(features.Feature, "to_shapely", to_shapely)
