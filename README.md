# android_location_converter
Converts the data file you get from Google Takeout to ESRI shapefile or GeoJSON.

When you download your personal data from Google Takeout, it comes in an Android proprietary format based on JSON.  This probably makes sense on Android/Google's end, but for us spatial data nerds, it's not so nice.  This script will take a Location History data file from Google Takeout and spit it back out as an ESRI Shapefile, GeoJSON or (non-attributed) KML.  KML is a pain to get attributes into so for now it may be best to convert to shp or geojson and then convert to KML from there with QGIS or something.

How to use it:

1. Make sure you have GDAL/OSGEO installed, as well as their python bindings.  These are geographic data transformation libraries that are required for this script to run.

2. Run it from cmd like this:

  python read_location_data.py path_to_location_history_file output_folder output_file_name output_file_type
  
  Parameters:
  
    path_to_location_history_file (string) - Path to the location history file.  You can get yours here: https://takeout.google.com/settings/takeout?utm_source=ob&utm_campaign=takeout&hl=en
  
    output_folder (string) - Path to the folder to write the output in.
  
    output_file_name (string) - What to name the output file.  You don't need to add a file extension but if you do, it will get ignored.
  
    output_file_type (string) - What type to write out to.  Currently there are only two options, "ESRI_Shapefile", "GeoJSON" and "KML"
    
Other miscellaneous notes:

You might notice that the date and time fields are written twice, once as an actual date datatype, and once again as a string.  This is because I was inspecting my output using QGIS, which seems to have some issues when querying date columns.  So the date string field is just there as a fallback.

I don't completely understand what the "sub timestamp" and "sub date" fields represent.  The "sub" ones are buried in the original JSON along with the activities and confidence levels, but I wanted to be comprehensive so I ripped them out with everything else.
