import geoiq

# Create with username/password
gq = geoiq.GeoIQ("http://demo.geoiq.com/","danshoutis","REDACTED")

# alternatively:
# GeoCommons = geoiq.GeoIQ() # defaults + no login = geocommons.com

# Search: three pages of two per page, keyword is 'peace':
# =====================================================
def search_example():
    for rp in gq.search("peace",per_page=2,page_limit=3):
        print("================ Page ==============")
        print("Total results: %d" % rp.totalResults)
        for o in rp.entries:
            try:
                d = o.load() # fetch the actual dataset (or map!)
                if (o.is_dataset):
                    print("%s -- %d features" % (dataset.title, dataset.feature_count))
                if (o.is_map):
                    # ..
                    pass

# Dataset creation:
# =============================
def create_example():
    # path to data, or a feed URL, is mandatory:
    # d = gq.datasets.create("http://...")
    d = gq.datasets.create('/path/to/cities.shp')
    d.name="Test shapefile upload."
    d.save()
    print("Uploaded! Results:")
    print(repr(d.props))

create_example()
    
