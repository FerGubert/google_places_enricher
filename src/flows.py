from config import RADIUS, NORTHEAST_LAT, NORTHEAST_LON, SOUTHWEST_LAT, SOUTHWEST_LON
from utils import *
import time
import shapely.geometry
import pyproj

def calculate_coordinates():
    """
    Generates a csv file with the geographic coordinates of a rectangular area 
    and according to a predetermined step in meters.

    Parameters
    ----------
    No Parameters.

    Raises
    ------
    No raises.

    Returns
    -------
    str
        Message indicating the end of execution.
    """

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

    with open('data/output/lat_lon_calculated.csv', 'w') as of:
        of.write('lat;lon\n')
        for p in gridpoints:
            of.write('{:f};{:f}\n'.format(p.x, p.y))

    return 'Execution performed successfully.'

def request_google_places():
    """
    Performs requests to the Google places API, according to the geographic coordinates
    defined in the input file and a predetermined radius. 
    It enriches the data according to the categories also defined in the input file
    and handles the return of the API, making the data available in a csv file.

    Parameters
    ----------
    No Parameters.

    Raises
    ------
    FileNotFound
        If the coordinates or categories file is not found in the target folder.
    ErrorStatusMessage
        if the Google places API return has a status other than OK.

    Returns
    -------
    str
        Message indicating if the flow was executed successfully or 
        otherwise the error that interrupted the execution.
    """

    df_latlon = read_file('Coordinates', 'data/input/lat_lon.csv')
    if type(df_latlon)==str:
        return df_latlon

    df_categories = read_file('Categories', 'data/input/categories_request.csv')
    if type(df_categories)==str:
        return df_categories
    if len(df_categories) == 0:
        df_categories.loc[0] = ['']

    establishments_features_data, establishments_features_labels = initialize_variables_request()

    for lat_lon in df_latlon.iterrows():
        lat = lat_lon[1]['lat']
        lon = lat_lon[1]['lon']
        
        for cat in df_categories['category']:
            establishments = []

            url = create_url_request(lat, lon, cat)
            results = make_request(url)
            if not results['status'] == 'OK':
                export_data_request(establishments_features_labels, establishments_features_data)
                return '[ERROR] {:s}: {:s}\nHowever the data that could be collected were exported.'\
                        .format(results['status'], results['error_message'])

            establishments.extend(results['results'])

            pages = 1
            params = {}
            time.sleep(2)
            while "next_page_token" in results:
                pages += 1
                params['pagetoken'] = results['next_page_token']
                results = make_request(url, params)
                if not results['status'] == 'OK':
                    export_data_request(establishments_features_labels, establishments_features_data)
                    return '[ERROR] {:s}: {:s}.\nHowever the data that could be collected were exported.'\
                            .format(results['status'], results['error_message'])
                establishments.extend(results['results'])
                time.sleep(2)

            for establishment in establishments:

                for feature_index in range(len(establishments_features_labels)-1):
                    try:
                        establishments_features_data[feature_index]\
                        .append(establishment[establishments_features_labels[feature_index]])
                    except:
                        establishments_features_data[feature_index].append(None)
                
                establishments_features_data[len(establishments_features_data)-1].append(cat)


    export_data_request(establishments_features_labels, establishments_features_data)
    return 'Execution performed successfully.'

def match_category_phrases():
    """
    Creates the Yelp phrases using the category hierarchical levels and creates the establishment phrases 
    using the Google categories and the enrichment categories. The records of establishments with their phrases are exported in a csv file. 
    Then, for each sentence of the establishment, it retrieves the Yelp sentence with the highest semantic textual similarity, 
    making these matchings available with their respective scores in a csv file.

    Parameters
    ----------
    No Parameters.

    Raises
    ------
    No Raises.

    Returns
    -------
    str
        Message indicating the end of execution.
    """

    df_categories_yelp = read_file('Hierarchical Yelp categories', 'data/input/hierarchical_yelp_categories.csv')
    df_categories_yelp['phrase_yelp'] = create_yelp_phrase(df_categories_yelp)

    df_estab = read_file('Establishments', 'data/output/establishments.csv')
    df_categories_estab_phrases = create_estab_phrase(df_estab)

    df_estab_phrases = df_categories_estab_phrases.merge(df_estab, on='place_id', how='left')
    df_estab_phrases.drop(columns=['categories', 'types'], inplace=True)
    df_estab_phrases.to_csv('data/output/establishments_phrases.csv', index=False)

    df_estab_phrases_uniques = df_categories_estab_phrases.drop_duplicates(subset="phrase_establishment")[['phrase_establishment']]
    df_estab_phrases_uniques['words_phrase_estab'] = df_estab_phrases_uniques['phrase_establishment'].apply(lambda frase: len(frase.split(' ')))
    df_estab_phrases_uniques = df_estab_phrases_uniques[df_estab_phrases_uniques['words_phrase_estab'] > 1]

    df_score = calculate_similarity_sentences(df_estab_phrases_uniques['phrase_establishment'], df_categories_yelp['YelpPhrase'])
    df_score.to_csv('data/output/matching_category_phrases.csv', index=False)

    return 'Execution performed successfully.'