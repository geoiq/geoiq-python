# python-geoiq

    TODO: description below needs proofing/rewriting/buy-in from geoiq

This is a python wrapper for the GeoIQ API. It allows Python developers to build unique and powerful domain specific applications. The API provides capability for uploading and download data, searching for data and maps, building, embedding, and theming maps or charts, as well as general user, group, and permissions management.

1\.  [Installation](#installation)  
1.1\.  [Using easy_install](#usingeasy_install)  
1.2\.  [On windows](#onwindows)  
1.3\.  [Optional functionality](#optionalfunctionality)  
2\.  [Usage](#usage)  
2.1\.  [Connecting to GeoIQ](#connectingtogeoiq)  
2.2\.  [Searching for data and maps](#searchingfordataandmaps)  
2.3\.  [Working with datasets](#workingwithdatasets)  
2.3.1\.  [Accessing feature data](#accessingfeaturedata)  
2.3.2\.  [Downloading a dataset](#downloadingadataset)  
2.4\.  [Working with maps](#workingwithmaps)  
2.5\.  [Analysis](#analysis)  
2.5\.  [Users and groups](#usersandgroups)  

<a name="installation"></a>

## 1\. Installation

<a name="usingeasy_install"></a>

### 1.1\. Using easy_install

    easy_install geoiq

<a name="onwindows"></a>

### 1.2\. On windows

    TODO: needs testing/validation!

The easiest method is to use easy_install. If you don't have it already:

* Download and run the windows .exe installer for setuptools for your version of python from: http://pypi.python.org/pypi/setuptools

* From the command prompt, run `C:\python2.5\scripts\easy_install.exe geoiq`, with `C:\python2.5\` replaced by your python installation location if needed.

<a name="optionalfunctionality"></a>

### 1.3\. Optional functionality

If you want to use [Shapely](http://trac.gispython.org/lab/wiki/Shapely) with geoiq, make sure that Shapely is installed. On windows, use its installer (which includes DLLs that Shapely requires); on other platforms, you must ensure that `libgeos_c` is present.

<a name="usage"></a>

## 2\. Usage

<a name="connectingtogeoiq"></a>

### 2.1\. Connecting to GeoIQ

    import geoiq

    # Connection to geocommons.com:
    geocommons = geoiq.GeoIQ()
    
    # Connect to a GeoIQ account:
    gq = geoiq.GeoIQ("http://demo.geoiq.com/", "username", "password")
   
    # Geocommons.com as a logged-in user:
    geocommons_loggedin = geoiq.GeoIQ("http://geocommons.com/", "username", "password")
    
<a name="searchingfordataandmaps"></a>

### 2.2\. Searching for data and maps

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
    
<a name="workingwithdatasets"></a>

### 2.3\. Working with datasets

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

<a name="accessingfeaturedata"></a>

#### 2.3.1\. Accessing feature data

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
	
    
<a name="downloadingadataset"></a>

#### 2.3.2\. Downloading a dataset

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


<a name="workingwithmaps"></a>
### 2.4\. Working with maps

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
     # ... further style editing ...
     new_map.save()
     

<a name="analysis></a>
#### 2.5\. Analysis

     TODO: need documentation for analyses & params!!

To run a GeoIQ analytical operation, first load available analyses:

     geoiq.analysis.load_all_analyses()
     
Then, use the analysis of your choice:

     analysis_result_dataset = geoiq.analysis.analyze_intersect(ds1=a, ds2=b)
     




<a name="usersandgroups"></a>

### 2.6\. Users and groups

     user = geoiq.users.get_by_username("foo")
     
     group = geoiq.groups.get_by_id(1234)
     
     # ... TODO, convenience wrappers for membership & permissions: 
     #   group.add(user), group.remove(user),
     #   map_or_ds.permissions.view(user), # and .edit and .access
     #   map_or_ds.permissions.remove(user_or_group)
