# python-geoiq

    TODO: description below needs proofing/rewriting/buy-in from geoiq

This is a python wrapper for the GeoIQ API. It allows Python developers to build unique and powerful domain specific applications. The API provides capability for uploading and download data, searching for data and maps, building, embedding, and theming maps or charts, as well as general user, group, and permissions management.

!TOC

## Installation

### Using easy_install

    easy_install geoiq

### On windows

    TODO: needs testing/validation!

The easiest method is to use easy_install. If you don't have it already:

* Download and run the windows .exe installer for setuptools for your version of python from: http://pypi.python.org/pypi/setuptools

* From the command prompt, run `C:\python2.5\scripts\easy_install.exe geoiq`

### Optional functionality

If you want to use [Shapely](http://trac.gispython.org/lab/wiki/Shapely) with geoiq, make sure that Shapely is installed. On windows, use its installer (which includes DLLs that Shapely requires); on other platforms, you must ensure that `libgeos_c` is present.

## Usage

### Connecting to GeoIQ

    import geoiq

    # Connection to geocommons.com:
    geocommons = geoiq.GeoIQ()
    
    # Connect to a GeoIQ account:
    gq = geoiq.GeoIQ("http://demo.geoiq.com/", "username", "password")
   
    # Geocommons.com as a logged-in user:
    geocommons_loggedin = geoiq.GeoIQ("http://geocommons.com/", "username", "password")
    
### Searching for data and maps

General searching:

    search_results = geocommons.search("haiti", limit=30)
    for result in search_results:
        print(result.title)
	print(result.description)
	if (result.is_map()): # It's a map
	    pass
	if (result.is_dataset()): # It's a dataset
            pass
	
	the_map_or_dataset = result.load() # Load the result object

Searching for maps or datasets specifically:

    maps = geocommons.search.maps("haiti", limit = 30)
    datasets = geocommons.search.datasets("haiti")
    
Search by user:

    my_stuff = geocommons.search.by_username("my_username")
    
    # alternatively:
    my_stuff = geocommons.current_user.library()
    
### Working with datasets

You can fetch a dataset by ID or by searching. To get a dataset by ID:

    dataset = gecommons.datasets.get_by_id(1234)
    
A dataset can be created from the following file types:

* `.shp` -- ESRI shapefiles (Must have accompanying `.dbf` and `.shx`)
* `csv` 
* `rss` 
* `kmz` 
* `kml` 

They can also be created by the URL to a RSS, KML, ATOM or GeoRSS feed.

To create a dataset:

    dataset = gq.datasets.create("path/to/data")
    
    # alternatively:
    dataset = gq.datasets.create("http://url.of.feed/")
    
    dataset.title = "The title I'd like to give the dataset"
    
    # ... set other properties (description, tags, etc) ...
    
    dataset.save()
    
You can also update properties on an existing dataset.

    ds = gq.datasets.get_by_id(1234)
    
    ds.title = "Renamed dataset"
    ds.save()

#### Accessing feature data

You can pull out the features & attributes of a dataset:

    feats = dataset.features()
    for feature in feats:
        # Hex-encoded well-known binary
        raw_geometry = feature.geometry
	
	# Feature attributes:
	name = feature.attributes["name"]
	
	# If you have shapely:
	shapely_geometry = feature.to_shapely()
	
	# If you're on windows with ArcGIS:
	arc_geometry_array = feature.to_arc() # TODO not yet implemented
	
    
#### Downloading a dataset

You can download a dataset in the format of your choice:

    shapefile, other_files = dataset.download_shapefile("/path/to/folder")
    # shapefile is the path to the .shp
    # other_files is an array with the names of the .shx, .dbf, .prj, etc
    
    kmlfile = dataset.download("/path/to/dataset.kml", "kml")
    
Supported formats are:

* `kml`
* `csv`
* `rss`
* `zip` -- a zipped shapefile

#### Analyzing a dataset.

     TODO: need documentation for analyses & params!!

To run a GeoIQ analytical operation:

     analysis_result_dataset = dataset.analylze("algorithm_name", { "param1":123 })
     

### Working with maps

Getting a map:

     my_map = geoiq.maps.get_by_id(1234)
     
Creating a map:

     new_map = geoiq.maps.create()
     new_map.title = "My map"
     new_map.save()
     layer = new_map.add_layer(dataset)
     layer.title="First layer"
     new_map.save()
     
Working with layer styles:

     top = new_map.layers[0]
     top.styles["stroke"]["color"] = 0 # make it black
     # ... style editing ...
     new_map.save()
     
### Users and groups

     user = geoiq.users.get_by_username("foo")
     
     group = geoiq.groups.get_by_id(1234)
     
     # ... TODO, convenience wrapper for permissions: 
     #   group.add(user), group.remove(user),
     #   map_or_ds.permissions.view(user), # and .edit and .access
     #   map_or_ds.permissions.remove(user_or_group)
