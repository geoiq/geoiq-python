
import geoiq, jsonwrap

class DatasetSvc(geoiq.GeoIQSvc):
    name="datasets"
    by_id = "datasets/{id}.json?include_features=0"
    create = "datasets"
    update_feed = "datasets/{id}/fetch.json"

    
    def get_entity(self,json):
        return Dataset

    def request_feed_update(self, ds):
        u = self.url(update_feed, ds)
        r,_ = self.do_req(u, "GET", None, lambda x : x)
        return r
    


class Dataset(geoiq.GeoIQObj):
    iqprops = geoiq.props("title",
                          "description",
                          "tags",
                          "published",
                          "data_type",
                          "feature_count",
                          "link")

    def request_feed_update(self):
        service.request_feed_update(self)

