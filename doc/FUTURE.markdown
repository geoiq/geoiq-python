# Nice things to have in the future:

* An endpoint to determine GeoIQ's API version.

* Dataset state ('processing'), etc. as part of a dataset's properties.

  * I'm not sure if this  is needed, but: if any operations (features;
    analysis; etc) will fail if the state is not 'complete', it's much
    more important!

* Much more documentation.

  * Recommendation: 

* Better internal errors (in particular, JSON 500 errors instead of HTML)

  * Recommendation: On a 500, return a UUID that's also logged to the
    server log (for internal troubleshooting)

* More specific error messages for bad inputs/requests, etc. "Dataset XYZ
  does not exist, so you can't analyze it" and analagous.
