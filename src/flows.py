from config import *
from utils import initialize_variables, make_request, export_data
import pandas as pd
import time
import shapely.geometry
import pyproj

def calculate_coordinates():
    to_proxy_transformer = pyproj.Transformer.from_crs('epsg:4326', 'epsg:3857')
    to_original_transformer = pyproj.Transformer.from_crs('epsg:3857', 'epsg:4326')

    sw = shapely.geometry.Point(SOUTHWEST_LAT, SOUTHWEST_LON)
    ne = shapely.geometry.Point(NORTHEAST_LAT, NORTHEAST_LON)

    stepsize = RADIUS*2

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

    return 'Execution performed successfully.'

def request_google_places():
    try:
        df_latlon = pd.read_csv('../data/input/latlon.csv', sep=';')
    except:
        return '[ERROR] Coordinate file not found.'
    if len(df_latlon) == 0:
        return '[ERROR] Empty coordinate file.'

    try:  
        df_categories = pd.read_csv('../data/input/categories.csv', sep=';')
    except:
        return '[ERROR] Category file not found.'
    if len(df_categories) == 0:
        df_categories.loc[0] = ['']

    establishments_features_data, establishments_features_labels = initialize_variables()

    radius = '&radius=' + RADIUS
    for lat_lon in df_latlon.iterrows():
        lat = lat_lon[1]['lat']
        lon = lat_lon[1]['lon']
        
        location = '&location=' + str(lat) + ',' + str(lon)
        
        for cat in df_categories['category']:
            establishments = []
            
            establishment_keyword = '&keyword=' + cat

            URL = GOOGLE_MAPS_API + API + SEARCH_COMPONENT + OUTPUT_TYPE + KEY + location + radius + establishment_keyword

            results = make_request(URL)
            if not results['status'] == 'OK':
                return '[ERROR] '+results['status']+': '+results['error_message']

            establishments.extend(results['results'])

            pages = 1
            params = {}
            time.sleep(2)
            while "next_page_token" in results:
                pages += 1
                params['pagetoken'] = results['next_page_token']
                results = make_request(URL, params)
                if not results['status'] == 'OK':
                    return '[ERROR] '+results['status']+': '+results['error_message']
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
    return 'Execution performed successfully.'