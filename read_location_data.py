from argparse import ArgumentParser
import datetime
import json
from os.path import join as osjoin, splitext
from osgeo import ogr
from osgeo.ogr import Feature, FieldDefn, Geometry, GetDriverByName, wkbPoint
from osgeo.osr import SpatialReference

def make_reader(in_json):

    # Open location history data
    json_data = json.loads(open(in_json).read())

    # Get the easy fields
    for item in json_data['locations']:
        date = datetime.datetime.fromtimestamp(int(item['timestampMs'])/1000).strftime('%Y-%m-%d')
        timestamp = datetime.datetime.fromtimestamp(int(item['timestampMs'])/1000).strftime('%H:%M:%S')
        longitude = item['longitudeE7']/10000000.0
        latitude = item['latitudeE7']/10000000.0
        accuracy = item['accuracy']

    # If there are any recorded activities in this entry, pick them apart by navigating through the json
        try:
            activities = build_field_dict(item['activitys'][0]['activities'])
            sub_date = datetime.datetime.fromtimestamp(int(item['activitys'][0]['timestampMs'])/1000).strftime('%Y-%m-%d')
            sub_timestamp = datetime.datetime.fromtimestamp(int(item['activitys'][0]['timestampMs'])/1000).strftime('%H:%M:%S')
        except:
            activities = None

        yield [date, timestamp, sub_date, sub_timestamp, longitude, latitude, accuracy, activities]

def build_field_dict(in_dict):

    # This converts the list of dictionaries holding confidence values into one dictionary mapping each activity to its
    # respective confidence.
    return dict((in_dict['type'], in_dict['confidence']) for in_dict in in_dict)

def setup_fields(in_layer):

    # Create all the fields that will exist in the output data
    date_field = FieldDefn('Date', ogr.OFTDate)
    in_layer.CreateField(date_field)

    date_sub_field = FieldDefn('Date_Sub', ogr.OFTDate)
    in_layer.CreateField(date_sub_field)

    date_str_field = FieldDefn('Date_Str', ogr.OFTString)
    date_str_field.SetWidth(10)
    in_layer.CreateField(date_str_field)

    date_sub_str_field = FieldDefn('DateSubStr', ogr.OFTDate)
    in_layer.CreateField(date_sub_str_field)

    timestamp_field = FieldDefn('Time', ogr.OFTString)
    timestamp_field.SetWidth(8)
    in_layer.CreateField(timestamp_field)

    timestamp_sub_field = FieldDefn('Time_Sub', ogr.OFTString)
    timestamp_sub_field.SetWidth(8)
    in_layer.CreateField(timestamp_sub_field)

    longitude_field = FieldDefn('Longitude', ogr.OFTString)
    in_layer.CreateField(longitude_field)

    latitude_field = FieldDefn('Latitude', ogr.OFTString)
    in_layer.CreateField(latitude_field)

    accuracy_field = FieldDefn('Accuracy', ogr.OFTInteger)
    in_layer.CreateField(accuracy_field)

    for confidence_field in ['still', 'tilting', 'inVehicle', 'onBicycle', 'walking', 'onFoot', 'unknown']:
        add_field = FieldDefn(confidence_field, ogr.OFTInteger)
        in_layer.CreateField(add_field)

def fill_fields(in_feature, in_entry):

    # Fill out all the data using the proper item yielded by the reader
    in_feature.SetField('Date', in_entry[0])
    in_feature.SetField('Date_Sub', in_entry[2])
    in_feature.SetField('Date_Str', in_entry[0])
    in_feature.SetField('DateSubStr', in_entry[2])
    in_feature.SetField('Time', in_entry[1])
    in_feature.SetField('Time_Sub', in_entry[3])
    in_feature.SetField('Longitude', in_entry[4])
    in_feature.SetField('Latitude', in_entry[5])
    in_feature.SetField('Accuracy', in_entry[6])

    for confidence_field in ['still', 'tilting', 'inVehicle', 'onBicycle', 'walking', 'onFoot', 'unknown']:
        try:
            in_feature.SetField(confidence_field, in_entry[7][confidence_field])
        except:
            pass

def write_output(in_reader, out_location, out_name, out_type):

    # Set up file to write to
    feature_index = 0
    spatial_reference = SpatialReference()
    spatial_reference.ImportFromEPSG(4326)
    driver = GetDriverByName(out_type)
    if out_type == 'ESRI Shapefile':
        out_data = driver.CreateDataSource('{0}.shp'.format(splitext(osjoin(out_location, out_name))[0]))
    elif out_type == 'GeoJSON':
        out_data = driver.CreateDataSource('{0}.geojson'.format(splitext(osjoin(out_location, out_name))[0]))
    elif out_type == 'KML':
        out_data = driver.CreateDataSource('{0}.kml'.format(splitext(osjoin(out_location, out_name))[0]))
    out_layer = out_data.CreateLayer('layer', spatial_reference, wkbPoint)

    # Set up fields
    setup_fields(out_layer)

    # Set Layer definition
    layer_definition = out_layer.GetLayerDefn()

    # Add points as they are processed by the reader
    for entry in in_reader:

        point = Geometry(wkbPoint)
        point.SetPoint(0, entry[4], entry[5])
        feature = Feature(layer_definition)
        feature.SetGeometry(point)

        # Increment FID value if it is a shp output
        if out_type == 'ESRI Shapefile':
            feature_index += 1
            feature.SetFID(feature_index)

        # Fill out all other fields
        fill_fields(feature, entry)

        # Add the feature to the layer
        out_layer.CreateFeature(feature)

        # Cleanup
        feature.Destroy()
        point.Destroy()

    # Big cleanup
    out_data.Destroy()

def init_parser():

    parser = ArgumentParser(description="Convert Google Takeout Data")
    parser.add_argument('location_history_file', type=str,
                        help='Path to location history file to analyze.  Is usually named "LocationHistory.json"')
    parser.add_argument('output_location', type=str, help='Path to folder to write output')
    parser.add_argument('output_name', type=str, help='Name of output file')
    parser.add_argument('output_type', type=str,
                        help='"Output data type.  Valid types are "ESRI_Shapefile" and"GeoJSON"')

    return parser

def main():

    parser = init_parser()
    args = parser.parse_args()
    reader = make_reader(args.location_history_file)
    if args.output_type in ['ESRI_Shapefile','GeoJSON','KML']:
        write_output(reader, args.output_location, args.output_name, args.output_type.replace('_', ' '))
        print('Success')
    else:
        print('Output type not recognized.  Recognized values are "ESRI_Shapefile", "GeoJSON" and "KML".')

if __name__ == '__main__':
    main()
