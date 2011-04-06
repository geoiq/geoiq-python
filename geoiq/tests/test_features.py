import unittest as ut
import geoiq.features as features
import binascii, random
import shapely.geometry
import shapely.wkb

class repeated(object):
    def __init__(self, count):
        self.count = count

    def __call__(self, f):
        def r(*args,**kwargs):
            for x in range(self.count):
                f(*args,**kwargs)
        return r

class TestFeatures(ut.TestCase):
    
    @repeated(1000)
    def test_point_roundtrip(self):
        self.wkb_roundtrip(shapely.geometry.Point(*self.point()))
        
    @repeated(100)
    def test_linestr_roundtrip(self):
        points = self.line_ring()
        self.wkb_roundtrip(shapely.geometry.LineString(points))

    @repeated(100)
    def test_polygon_roundtrip(self):
        parts = self.poly()
        hd = parts[0]
        rst = parts[1:]
        self.wkb_roundtrip(shapely.geometry.Polygon(hd,rst))

    @repeated(1000)
    def test_multipoint_roundtrip(self):
        self.wkb_roundtrip(self.multi(self.point, shapely.geometry.MultiPoint))
                    

    def wkb_roundtrip(self, geom):
        # Test our WKB parsing by round-tripping through Shapely
        s = geom.wkb
        
        shapely_check = shapely.wkb.loads(geom.wkb)
        self.assertEquals(s, shapely_check.wkb, "Shapely/geos bug?")
        
        f = features.Feature({"geometry":binascii.b2a_hex(s)})
        ignored, nshape = f.to_shapely()

        self.assertEquals(s, nshape.wkb, "WKB representation diverged?\n%s\n======\n%s\n" % (binascii.b2a_hex(s), binascii.b2a_hex(nshape.wkb)))
    
    def point(self):
        return (random.uniform(-90.0, 90.0),
                random.uniform(-180.0, 180.0))

    def line_ring(self, closed=False):
        c = random.randint(1,2000)
        if closed:
            c = random.randint(3,2000)
        points = [self.point() for x in range(c)]
        if (closed):
            points.append(points[0])
        return points

    def poly(self):
        c = random.randint(1,10)
        parts = [self.line_ring(True)  for i in range(c) ]
        return parts

    def multi(self, inner, shply_class):
        c = random.randint(1,15)
        geoms = [ inner() for x in range(c) ]
        return shply_class(geoms)

