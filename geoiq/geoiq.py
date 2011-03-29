##
# Base...
import urllib2 as u
import urllib
import base64, sys
import jsonwrap

# TODO: multipart:
# http://atlee.ca/software/poster/index.html

# http://code.activestate.com/recipes/146306-http-client-to-post-using-multipartform-data/
# http://stackoverflow.com/questions/680305/using-multipartposthandler-to-post-form-data-with-python

try: import simplejson as json
except ImportError : import json

class GeoIQ(object):
    def __init__(self, root="http://geocommons.com/",
                 username=None, password=None):

        self.endpoint = GeoIQEndpoint(root,username,password)

        for tp in GeoIQSvc.__subclasses__():
            setattr(self, tp.name, tp(self.endpoint))
            

class GeoIQEndpoint(object):
    def __init__(self, root, username, password):
        self.root = root
        self.username = username
        self.password = password

    def add_auth(self,req):
        if self.username is None:
            return req
        auth = base64.encodeString("%s:%s" % (username,password))[:-1]
        req.add_header("Authorization", "Basic %s" % auth)
        return req

    def resolve(self, path, verb, data=None):
        req = u.Request(self.root + path, data)
        req.get_method = lambda: verb
        print("Request " + verb +":" + self.root + path)
        return self.add_auth(req)
    
class GeoIQSvc(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_entity(self,json):
        raise NotImplementedError()

    def generate_entity(self, json, cls=None):
        if cls is None: cls = self.get_entity(json)

        return cls.map(json, self)


    def unwrapper(self, r):
        return self.generate_entity(r)

    def url(self, p, obj):
        return (p.format(**url_dict(getattr(obj, 'props', obj))))

    def do_req(self, path, verb, obj, unwrapper=None):
        if unwrapper is None: unwrapper = self.unwrapper
        if (obj):
            obj = json.dumps(obj.props)
        
        req = self.endpoint.resolve(path, verb, obj)
        
        # TODO Error handling
        res = json.load(u.urlopen(req))
        fin = unwrapper(res)

        return fin,res

    def get_by_id(self, geoiqid):
        pass
    
    def create(self):
        pass
    
    def delete(self, obj):
        pass

    def update(self, obj):
        pass

def url_dict(d):
    return dict( ((k,urllib.quote(str(v))) for (k,v) in d.iteritems()) )

class GeoIQObj(jsonwrap.JsonWrappedObj):
    """
    Base class for GeoIQ's RESTful entities (things with an ID)
    """


    @classmethod
    def is_ro(cls): return False

    def __init__(self, props, svc = None):
        jsonwrap.JsonMappedObj.__init__(self,props)
        self.svc = svc
        assert(self.geoiq_id is not None)

    def refresh(self, lose_mods=False):
        if self.dirty() and not lose_mods:
            raise RuntimeError("Refreshing a dirty object")
    
        self.props = self.__class__.service.get_by_id(self.geoiq_id).props
        self.isdirty = false
        return self

    def save(self):
        pass
    
    def delete(self):
        pass

jsonwrap.props(GeoIQObj,geoiq_id={'ro':True, 'mapto':'id'})
