import geoiq, util.jsonwrap

class GroupSvc(geoiq.GeoIQSvc):
    create_url = "groups.json"
    by_id_url = "groups/$(id)s.json"

    def get_entity(self,json):
        return Group

geoiq.GeoIQ.regsvc("groups", GroupSvc)

class Group(geoiq.GeoIQObj):
    writeable=True
    pass

util.jsonwrap.props(Group, "name")
