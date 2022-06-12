from config import *
from utils import read_csv, initialize_variables, make_request, export_data
import time
import argparse
import shapely.geometry
import pyproj

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--radius', dest='radius')
    parser.add_argument('--northeast_lat', dest='northeast_lat')
    parser.add_argument('--northeast_lon', dest='northeast_lon')
    parser.add_argument('--southwest_lat', dest='southwest_lat')
    parser.add_argument('--southwest_lon', dest='southwest_lon')
    args = parser.parse_args()

    return args

def calculate_coordinates(radius, northeast_lat, northeast_lon, southwest_lat, southwest_lon):
    to_proxy_transformer = pyproj.Transformer.from_crs('epsg:4326', 'epsg:3857')
    to_original_transformer = pyproj.Transformer.from_crs('epsg:3857', 'epsg:4326')

    sw = shapely.geometry.Point(southwest_lat, southwest_lon)
    ne = shapely.geometry.Point(northeast_lat, northeast_lon)

    stepsize = radius*2

    transformed_sw = to_proxy_transformer.transform(sw.x, sw.y)
    transformed_ne = to_proxy_transformer.transform(ne.x, ne.y)

    gridpoints = []
    x = transformed_sw[0] + stepsize
    while x < transformed_ne[0]:
        y = transformed_sw[1] + stepsize
        while y < transformed_ne[1]:
            p = shapely.geometry.Point(to_original_transformer.transform(x, y))
            gridpoints.append(p)
            y += stepsize
        x += stepsize

    with open('../data/output/lat_lon_calculated.csv', 'w') as of:
        of.write('lat;lon\n')
        for p in gridpoints:
            of.write('{:f};{:f}\n'.format(p.x, p.y))

def request_google_places(radius):
    df_latlon = read_csv('../data/input/latlon.csv')
    df_categories = read_csv('../data/input/categories.csv')

    establishments_features_data, establishments_features_labels = initialize_variables()

    radius = '&radius=' + radius
    for lat_lon in df_latlon.iterrows():
        lat = lat_lon[1]['lat']
        lon = lat_lon[1]['lon']
        
        location = '&location=' + str(lat) + ',' + str(lon)
        
        for cat in df_categories['category']:
            establishments = []
            
            establishment_keyword = '&keyword=' + cat

            URL = GOOGLE_MAPS_API + API + SEARCH_COMPONENT + OUTPUT_TYPE + KEY + location + radius + establishment_keyword

            results = make_request(URL)
            establishments.extend(results['results'])

            pages = 1
            params = {}
            time.sleep(2)
            while "next_page_token" in results:
                pages += 1
                params['pagetoken'] = results['next_page_token']
                results = make_request(URL, params)
                establishments.extend(results['results'])
                time.sleep(2)

            for establishment in establishments:

                for feature_index in range(len(establishments_features_labels)-1):
                    try:
                        establishments_features_data[feature_index].append(establishment[establishments_features_labels[feature_index]])
                    except:
                        establishments_features_data[feature_index].append(None)
                
                establishments_features_data[len(establishments_features_data)-1].append(cat)

    export_data(establishments_features_labels, establishments_features_data)

if __name__== "__main__" :
    
    args = main()
    if (args.radius != None) and (args.northeast_lat != None) and (args.northeast_lon != None) and (args.southwest_lat != None) and (args.southwest_lon != None):
        calculate_coordinates(args.radius, args.northeast_lat, args.northeast_lon, args.southwest_lat, args.southwest_lon)
    elif args.radius != None:
        request_google_places(args.radius)
    else:
        # erro
        pass


