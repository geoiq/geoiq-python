import geoiq.jsonwrap as jsonwrap
import struct, binascii

def parse_geometry(geometry, factory):
    bindat = binascii.a2b_hex(geometry)
    return parse_geometry_imp(bindat,factory)

def parse_geometry_imp(bindat, factory):
    ofs = [0] # smuggle into an array b/c of Python's scoping.
    byteorder = ""

    # http://edndoc.esri.com/arcsde/9.0/general_topics/wkb_representation.htm
    def chomp(fmt):
        r = struct.unpack_from(byteorder + fmt, bindat, ofs[0])
        ofs[0] = ofs[0] + struct.calcsize(fmt)
        return r

    def point(kind=None):
        a,b = chomp("dd")
        return factory.point(kind, a,b)

    def linear_ring():
        c = chomp("I")[0]
        for x in range(c):
            yield (point())
            
    def linestring(kind):
        return factory.linestring(kind, linear_ring())

    def polygon(kind):
        part_c = chomp("I")[0]
        
        return factory.polygon(kind, ((factory.linestring(kind,linear_ring())) for i in range(part_c)))


    def geometry_collection(k=None):
        # 1) Read the byte order:
        bo = chomp("B")

        if (bo == 0):
            byteorder = ">" # network (big-endian) byte order
        else:
            byteorder = "<" # Little-endian byte order

        # 2) Geometry kind:
        rawkind = chomp("I")[0]

        kind, parse_f,multi = {
            1 : ("point",point,False),
            2 : ("linestring",linestring,False),
            3 : ("polygon",polygon,False),
            4 : ("multipoint",point,True),
            5 : ("multilinestring",linestring,True),
            6 : ("multipolygon",polygon,True),
            7 : ("geometrycollection", geometry_collection, True)
            }[rawkind]

        if not multi:
            return parse_f(kind)

        multi_count = chomp("I")[0]
        parse_f = geometry_collection
        return factory.multi(kind, [parse_f(kind) for r in range(multi_count)])

    return geometry_collection()

class Feature(jsonwrap.JsonWrappedObj):
    def raw_parse(self, fact):
        return parse_geometry(self.geometry, fact)

    def attributes(self):
        r = dict( (p,v) for (p,v) in self.props.iteritems() if p != 'geometry')
        return r

jsonwrap.props(Feature,
               "geometry")
