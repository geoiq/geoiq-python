
import urllib2 as u, poster.encode, poster.streaminghttp 
import urllib
import base64, sys
import jsonwrap
try: import simplejson as json
except ImportError : import json



poster.streaminghttp.register_openers()

class GeoIQ(object):
    def __init__(self, root="http://geocommons.com/",
                 username=None, password=None):

        self.endpoint = GeoIQEndpoint(root,username,password)


    @classmethod
    def regsvc(cls, nm, svc):
        def getter(self):
            return svc(self, self.endpoint)

        setattr(cls, nm, property(getter))

def ident(x): return x

class GeoIQEndpoint(object):
    def __init__(self, root, username, password):
        self.root = root
        self.username = username
        self.password = password

    def add_auth(self,req):
        if self.username is None:
            return req
        auth = base64.encodestring("%s:%s" % (self.username,self.password))[:-1]
        req.add_header("Authorization", "Basic %s" % auth)
        return req

    def resolve(self, path, verb, data=None):
        # Filter out nulls
        if (data is not None):
            data = dict( (k,v) for (k,v) in data.iteritems() if v is not None)

        if (verb == "MULTIPART"): # use poster to do multipart form upload:
            assert(data is not None)
            datagen, headers = poster.encode.multipart_encode(data)
            req = u.Request(self.root + path, datagen, headers)
            return self.add_auth(req)

        # if post data is key-value pairs:
        if (data is not None):
            data = urllib.urlencode(data)
            

        req = u.Request(self.root + path, data)
        req.get_method = lambda: verb
        return self.add_auth(req)
    

class GeoIQSvc(object):
    def __init__(self, geoiq, endpoint):
        self.endpoint = endpoint
        self.geoiq = geoiq

    def get_entity(self,json):
        raise NotImplementedError()

    def generate_entity(self, json, cls=None):
        if cls is None: cls = self.get_entity(json)

        return cls.map(json, self)

    def unwrapper(self, r):
        return self.generate_entity(r)

    def url(self,p,query=None,**kargs):
        if (query is not None):
            if (hasattr(query, '__getitem__')):
                query = urllib.urlencode(dict( (k,v) for (k,v) in query.iteritems() if v is not None) )
                query = "?" + query
        if query is None: query = ""
        return p.format(**url_dict(kargs)) + query

    def obj_url(self, p, obj):
        return self.url(p, **obj.props)

    def raw_req(self,path,verb,postdata):
        return self.do_req(path,verb,postdata,unwrapper=ident,parser=ident)


    def do_req(self, path, verb, postdata, unwrapper=None, parser=json.load):
        if unwrapper is None: unwrapper = self.unwrapper
        
        req = self.endpoint.resolve(path, verb, postdata)
        
        # TODO tracing..
        try:
            v = u.urlopen(req)
        except u.HTTPError,e:
            handled,res = self.handle_error(e)
            if (handled): return (res,e)
            raise

        res = parser(v)
        fin = unwrapper(res)
        return fin,res


    def get_by_id(self, geoiqid):
        fin, res = self.do_req(self.url(self.__class__.by_id_url,
                                        id=geoiqid),
                               "GET",
                               None)
        return fin
    
    def refresh(self, obj):
        assert(obj.geoiq_id is not None)
        c = self.get_by_id(obj.geoiq_id)
        obj.props = c.props
        return obj

    def create(self):
        return self.get_entity(None)(None,self)
    
    def delete(self, obj):
        fin,res = self.do_req(self.url(self.__class__.by_id_url,
                                       id=obj.geoiq_id),
                              "DELETE",
                              None,
                              unwrapper=ident,
                              parser=ident)

        return fin,res

    def update_new(self,obj):
        fin,res = self.do_req(self.url(self.__class__.create_url),
                              "POST",
                              obj.unmap())
        obj.props = fin.props
        return obj

    def update(self, obj):
        if (obj.is_new()):
            return self.update_new(obj)
        fin,res = self.raw_req(self.url(self.__class__.by_id_url,
                                        id=obj.geoiq_id),
                               "PUT",
                               obj.unmap())
        return obj

    def handle_error(self, err):
        # On 404, return null:
        if (err.code == 404): return (True, None)

        if (err.code == 401): raise GeoIQAccessDenied(err.read())

        return (False,None)

def url_dict(d):
    return dict( ((k,urllib.quote(str(v))) for (k,v) in d.iteritems()) )

class GeoIQAccessDenied(Exception):
    pass

class GeoIQObj(jsonwrap.JsonWrappedObj):
    """
    Base class for GeoIQ's RESTful entities (things with an ID)
    """

    @classmethod
    def is_ro(cls): return False

    def __init__(self, props,svc):
        if props is None:
            props = {"id":None}
            self.__new = True
        else:
            self.__new = False

        jsonwrap.JsonWrappedObj.__init__(self,props)
        self.svc = svc
        self.geoiq = svc.geoiq
        
        assert(self.__new or self.geoiq_id is not None)

    def is_new(self):
        return self.__new

    def refresh(self, lose_mods=False):
        if self.dirty() and not lose_mods:
            raise RuntimeError("Refreshing a dirty object")
    
        self.props = self.svc.get_by_id(self.geoiq_id).props
        self.isdirty = False
        return self

    def save(self):
        r = self.svc.update(self)
        if r:
            self.__new = False
            self.isdirty = False
        return r

    def delete(self):
        r = self.svc.delete(self)
        self.props = None
        self.svc = None
        return r

jsonwrap.props(GeoIQObj,geoiq_id={'ro':True, 'mapto':'id'})
