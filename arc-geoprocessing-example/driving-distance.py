##
# GeoIQ python example:
#  Find driving distance!
#
# Requires: Network Analyst.
#
# HOWTO:
# ========
# Preparing a dataset from a shapefile:
#    http://webhelp.esri.com/arcgiSDEsktop/9.3/index.cfm?TopicName=Creating_a_network_dataset
#
# TODO: Programatically creating a network dataset?:
#   http://edndoc.esri.com/arcobjects/9.2/NET/06443414-d0a7-455d-a199-dfd49aca7d98.htm
# (No python geoprocessing support yet...)
# 
# * Instructions/discussion specific to on preparing a network from an
#   OSM shapefile extract (see answer #4):
#     http://forums.arcgis.com/threads/27196-Network-analysis-problem
#

import sys, os.path
import geoiq
# Create the geoprocessor object:
try:
    import arcgisscripting
    gp = arcgisscripting.create()
except ImportError:
    import win32com.client
    gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
def lg(m): gp.addMessage(m)

# Inputs:
#  1) the GeoIQ url
geoiq_url = sys.argv[1]

#  2 & 3) Username & password
username = sys.argv[2]
password = sys.argv[3]

#  4) The road network dataset to use
network_dataset = sys.argv[4]

#  5) The sites layer (Geoiq/geocommons URL or ID)
sites_layer = sys.argv[5]

#  6) Break distances: How far out from the site to generate travel
#     coverage polygons
breaks = " ".join(sys.argv[6].split(";"))

#  7) Impedance field name. Name of the field to use in the network
#     dataset for measuring travel -- length (distance) by default.
impedance_fld = sys.argv[7]

# 8)  Events layer.
events_layer = sys.argv[8]

#  9) Output folder -- where to store the final + intermediate results!
work_folder = sys.argv[9]

# 10) Title for the upload
upload_title = sys.argv[10]


# Connect to geoiq/geocommons:
gq = geoiq.GeoIQ(geoiq_url, username, password)

# Check out Network Analyst:
gp.CheckOutExtension("network")

# 0) Load the two datasets:
sites_ds = gq.datasets.get(sites_layer)
events_ds = gq.datasets.get(events_layer)
if sites_ds is None: raise ValueError("Couldn't get sites layer.")
if events_ds is None: raise ValueError("Couldn't get events layer.")
lg("Downloading sites.")
sites_shape = sites_ds.download_shapefile(work_folder)[0]
lg("Downloading events.")
events_shape = events_ds.download_shapefile(work_folder)[0]


# 1) Create service-area polygons for the sites layer:
# ============
svclayer = "GeoIQ_Site_Areas"

gp.MakeServiceAreaLayer_na(
    network_dataset, # in_network_dataset, 
    svclayer, # out_network_analysis_layer, 
    "Length", # impedance_attribute, 
    "TRAVEL_TO", # travel_from_to, 
    breaks, # default_break_values, 
    "DETAILED_POLYS", #polygon_type, 
    "NO_OVERLAP", # merge, 
    "RINGS", # nesting_type, 
    "NO_LINES", # line_type, 
    "OVERLAP", # overlap, 
    True, # split, 
    "", # excluded_source_name, 
    "", # accumulate_attribute_name, 
    "ALLOW_UTURNS", # UTurn_policy, 
    "", # restriction_attribute_name, 
    True, #polygon_trim, 
    "100 meters", # poly_trim_value, 
    False, #lines_source_fields
    )

lg("Adding locations")

gp.AddLocations_na(
    svclayer, # network_dataset, 
    "Facilities", 
    os.path.abspath(sites_shape),
    #"C:\\clients\\geoiq\\arc-geoprocessing-example\\outp\\evacuation_centers_from_japan_ushahidi.shp", #  
    "#", # Field mappings
    "100 meters", # search tolerance,
    "", # sort field,
    "", # custom snapping
    True, # "MATCH_TO_CLOSEST", # matching
    False, # "CLEAR",? 
    False, # snap facilities to roads?
    0)

lg("Solving")
gp.Solve_na(svclayer, True) # network_dataset, "SKIP")

output_polygons = os.path.join(work_folder, "distance_polys.shp")

# gp.SelectData_management(srclayer, "Polygons")
spatialRef = gp.Describe(svclayer + "\\Facilities").SpatialReference
gp.CreateFeatureclass_management(work_folder,
                                 "distance_polys.shp",
                                 "POLYGON",
                                 svclayer + "\\Polygons",
                                 "SAME_AS_TEMPLATE",
                                 "SAME_AS_TEMPLATE",
                                 spatialRef)

lg("Saving result")
gp.Append_management(svclayer + "\\Polygons",
                     output_polygons,
                     "NO_TEST")


ds = gq.datasets.create(output_polygons)
ds.title = upload_title 
lg("Uploading result polygons")
ds.save()

if not ds.compat_endpoint(events_ds):
    lg("Re-Uploading event points")
    new_events = gq.datasets.create(events_shape)
    new_events.copy_from(events_ds)
    new_events.save()
    events_ds = new_events

# Analyze them:
gq.analysis.load_all_analyses()
fin = gq.analysis.analyze_intersect(ds1=events_ds.geoiq_id,
                              ds2=ds.geoiq_id,
                              merge='combine')

# download final result
finshp = fin.download_shapefile(work_folder)[0]

