# android_location_converter
Converts the data file you get from Google Takeout to ESRI shapefile or GeoJSON.

When you download your personal data from Google Takeout, it comes in an Android proprietary format based on JSON.  This probably makes sense on Android/Google's end, but for us spatial data nerds, it's not so nice.  This script will take a Location History data file from Google Takeout and spit it back out as an ESRI Shapefile or GeoJSON.  I would like to add functionality for other formats (KML would be nice) but this has proven more difficult than anticipated.  For now enjoy them as shp or geojson, which are fairly universal.

How to use it:

1. Make sure you have GDAL/OSGEO installed, as well as their python bindings.  These are geographic data transformation libraries that are required for this script to run.

2. Run it from cmd like this:

  python read_location_data.py path_to_location_history_file output_folder output_file_name output_file_type
  
  Parameters:
  
    path_to_location_history_file (string) - Path to the location history file.  Pretty self-explanatory.
  
    output_folder (string) - Path to the folder to write the output in.
  
    output_file_name (string) - What to name the output file.  You don't need to add a file extension but if you do, it will get ignored.
  
    output_file_type (string) - What type to write out to.  Currently there are only two options, "ESRI_Shapefile" and "GeoJSON"
    
Other miscellaneous notes:

You might notice that the date field is written twice, once as an actual date datatype, and once again as a string.  This is because I was inspecting my output using QGIS, which seems to have some issues when querying date columns.  So the date string field is just there as a fallback.
