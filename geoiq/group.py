import geoiq, util.jsonwrap

class GroupSvc(geoiq.GeoIQSvc):
    create_url = "group_create_url"
    by_id_url = "group_by_id_url"

    def get_entity(self,json):
        return Group

geoiq.GeoIQ.regsvc("groups", GroupSvc)

class Group(geoiq.GeoIQObj):
    writeable=True
    pass

util.jsonwrap.props(Group, "name")
