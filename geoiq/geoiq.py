
import urllib2 as u, poster.encode, poster.streaminghttp 
import urlparse

import base64, sys
import util.jsonwrap as jsonwrap


try: import simplejson as json
except ImportError : import json

from util.protocol import *


poster.streaminghttp.register_openers()

class GeoIQ(object):
    def __init__(self, root="http://geocommons.com/",
                 username=None, 
                 password=None,
                 api_version=1.0):

        self.services = {}
        self.endpoint = GeoIQEndpoint(root,username,password)


    @classmethod
    def regsvc(cls, nm, svc):
        def getter(self):
            if nm not in self.services:
                self.services[nm] = svc(self, self.endpoint)
            return self.services[nm]

        setattr(cls, nm, property(getter))

def ident(x): return x

class GeoIQEndpoint(object):
    def __init__(self, root, username, password):
        if not root.endswith("/"):
            root = root + "/"
        self.root = root
        self.proot = urlparse.urlparse(root)
        self.username = username
        self.password = password

    def add_auth(self,req):
        if self.username is None:
            return req
        auth = base64.encodestring("%s:%s" % (self.username,self.password))[:-1]
        req.add_header("Authorization", "Basic %s" % auth)
        return req

    def resolve(self, path, verb, data=None):
        # Check to see if the path is relative OR at the same host:

        if self.shares_endpoint(path):
            use_auth = True
            if self.is_relative(path):
                path = self.root + path
        else:
            use_auth = False

        # Filter out nulls
        if (data is not None):
            data = obj_to_railsparams(data)

        if (verb == "MULTIPART"): # use poster to do multipart form upload:
            assert(data is not None)
            datagen, headers = poster.encode.multipart_encode(data)
            req = u.Request(path, datagen, headers)
            if use_auth: return self.add_auth(req)
            else: return req

        # if post data is key-value pairs:
        if (data is not None):
            data = urlencode_params(data)


        req = u.Request(path, data)
        req.get_method = lambda: verb
        if use_auth: return self.add_auth(req)
        else: return req

    def is_relative(self,url):
        pp = urlparse.urlparse(url)
        return pp.hostname is None

    def shares_endpoint(self, url):
        pp = urlparse.urlparse(url)
        if pp.hostname is not None:
            if pp.hostname != self.proot.hostname:
                return False
            else:
                return True
        else:
            return True

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
                query = urlencode_params(query)
                query = "?" + query

        if query is None: query = ""
        d = dict(**urlencode_dictvals(kargs))
        return (p % d) + query

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
            handled,res = self.handle_error(e, req, unwrapper, parser)
            if (handled): 
                return res
            else:
                print("Err %d:%s" % (e.code, req.get_full_url()))
                raise
        except u.URLError,e:
            print("Url error", req.get_full_url())
            raise

        res = parser(v)
        fin = unwrapper(res)
        return fin,res
    
    def get(self, v):
        # Get by ID or URL.
        try: id = int(v)
        except ValueError:
            return self.get_by_url(v)
        
        return self.get_by_id(id)


    def get_by_url(self, url):
        if self.endpoint.shares_endpoint(url):
            fin,res = self.do_req(self.url(url), "GET", None)
            print("downloading %s" % url)
            return fin
        else:
            up = urlparse.urlparse(url)
            other_endpoint = GeoIQEndpoint(urlparse.urlunparse((up.scheme,
                                                  up.netloc,
                                                  "",
                                                  "",
                                                  "",
                                                  "")), None, None)
            other_geoiq = GeoIQ()
            other_geoiq.endpoint = other_endpoint
            other_svc = self.__class__(other_geoiq, other_endpoint)
            return other_svc.get_by_url(url)


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
                              obj.to_json_obj())

        obj.props = fin.props
        return obj

    def update(self, obj):
        if (obj.is_new()):
            return self.update_new(obj)
        fin,res = self.raw_req(self.url(self.__class__.by_id_url,
                                        id=obj.geoiq_id),
                               "PUT",
                               obj.to_json_obj())
        return obj

    def handle_error(self, err, req, unwrapper, parser):
        # Python 2.5 (windows): 20x is an error.
        if (err.code >= 200 and err.code < 300):
            res = parser(err)
            fin = unwrapper(res)
            return (True,(fin,res))



        # On 404, return null:
        if (err.code == 404): return (True, (None,None))

        if (err.code == 401): 
            inf = "%s@%s ::" % (self.endpoint.username,req.get_full_url())
            raise GeoIQAccessDenied(inf + err.read())

        if (err.code == 400): 
            print("Bad request.")
            print("Request was:")
            print(req.get_method() + ":" + req.get_full_url())
            print(repr(req.get_data()))
            print("========")
            print(err.read())
            print("========")
            return (False, None)
            
        

        print("(err %d) on %s w/ %s" % (err.code, req.get_full_url(), req.get_data()))
        print("===")
        print err.read()
        print("===")

        return (False,None)

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

    def compat_endpoint(self,other):
        return self.svc.endpoint.shares_endpoint(other.svc.endpoint.root)

jsonwrap.props(GeoIQObj,geoiq_id={'ro':True, 'mapto':'id'})
