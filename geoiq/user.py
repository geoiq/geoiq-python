import geoiq, util.jsonwrap

class UserSvc(geoiq.GeoIQSvc):
    create_url = "user_create_url"
    by_id_url = "user_by_id_url"

    def get_entity(self,json):
        return User

    def get_by_login(self, login):
        return self.get_by_id(login)

    def create(self, 
               desired_name,
               password):
        u = User(None, self)
        u.props = {
            "login" : desired_name,
            "password" : password,
            "password_confirmation" : password
            }
        return u

    def current(self):
        if self.geoiq.endpoint.username is None: return None
        # NOTE: on demo.geoiq.com you can't look up stuff about yourself?

        return self.get_by_id(self.geoiq.endpoint.username)

geoiq.GeoIQ.regsvc("users", UserSvc)

def get_current_user(self):
    if self.endpoint.username is None: return None
    return UserStub(self.endpoint.username, self)

setattr(geoiq.GeoIQ, "current_user", property(get_current_user))

class UserStub(object):
    def __init__(self, username=None, geoiq=None):
        self.login = username
        self.geoiq = geoiq

    def _username(self): return self.login
    username = property(_username)

    def library(self, *args, **kargs):
        return self.geoiq.search.by_username(self.login, *args,**kargs)

    def maps(self, bbox=None, max_results=None):
        return self.library(model="map")

    def datasets(self, bbox=None, max_results=None):
        return self.library(model="dataset")

    def __str__(self):
        return "(geoiq user: %s)" % self.login

class User(geoiq.GeoIQObj, UserStub):
    writeable = True

    # Smuggle props into/out of the inner 'user' object:
    # --
    def to_json_obj(self):
        return { "User": geoiq.GeoIQObj.to_json_obj(self) }

    @classmethod
    def map(c,in_obj,*args,**kargs):
        return super(User,c).map(in_obj["User"], *args, **kargs)
    # --

util.jsonwrap.props(User,
                    "login",
                    "id",
                    "email",
                    "fullname",
                    "password",
                    "password_confirmation")
