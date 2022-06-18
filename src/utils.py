from config import *
import requests
import json
import pandas as pd
import os

def read_file(name, path_file, sep=';'):
    """
    Reads a csv file.

    Parameters
    ----------
    name: str
        Indicates the name of the file to be read.
    path_file: str
        Path of file to read.
    sep: str
        Csv file column separated.

    Raises
    ------
    FileNotFound
        If the file is not found in the path.

    Returns
    -------
    str
        Message indicating the error.
    pandas.DataFrame
        Dataframe with data read from csv file.
    """

    try:
        df = pd.read_csv(path_file, sep=sep)
    except:
        return '[ERROR] {:s} file not found.'.format(name)
    
    return df

def initialize_variables():
    """
    Initializes the main variables used in the google places API request.

    Parameters
    ----------
    No Parameters.

    Raises
    ------
    No Raises.

    Returns
    -------
    list, list
        A list of lists, where each one corresponds to one of the fields treated in the
        API's return, and a list of strings, corresponding to the names of these fields.
    """

    business_status,geometry,name,\
    opening_hours,place_id,price_level,\
    rating,types,user_ratings_total,\
    vicinity,category = ([], ) * 11

    establishments_features_data = [business_status, 
                                    geometry, name, 
                                    opening_hours, 
                                    place_id, 
                                    price_level, 
                                    rating, 
                                    types, 
                                    user_ratings_total, 
                                    vicinity, 
                                    category]

    establishments_features_labels = ['business_status', 
                                    'geometry', 
                                    'name', 
                                    'opening_hours', 
                                    'place_id', 
                                    'price_level', 
                                    'rating', 
                                    'types', 
                                    'user_ratings_total', 
                                    'vicinity', 
                                    'category']

    return establishments_features_data, establishments_features_labels

def create_url(lat, lon, cat):
    """
    Creates the url that will be used to make the request to the google places API.

    Parameters
    ----------
    lat: float
        Geographic coordinate latitude.
    lon: float
        Geographic coordinate longitude.
    cat: str
        Category for data enrichment.

    Raises
    ------
    No Raises.

    Returns
    -------
    str
        Url for the request in the google places API.
    """

    location = '&location={:s},{:s}'.format(str(lat), str(lon))
    radius = '&radius={:s}'.format(str(RADIUS))
    establishment_keyword = '&keyword={:s}'.format(cat)
    api_key = '&key={:s}'.format(os.getenv('KEY'))

    return GOOGLE_MAPS_API + API + SEARCH_COMPONENT + OUTPUT_TYPE + api_key + location + radius + establishment_keyword

def make_request(url, params={}):
    """
    Make the request to the google places API.

    Parameters
    ----------
    url: str
        Url for the request in the google places API.
    params: dict
        Parameters passed in the request.

    Raises
    ------
    No Raises.

    Returns
    -------
    dict
        API return with data and status.
    """

    res = requests.get(url, params = params)
    results = json.loads(res.content)
    return results

def export_data(establishments_features_labels, establishments_features_data):
    """
    Save data in csv file.

    Parameters
    ----------
    establishments_features_labels: list
        A list of strings with column names from the csv file.
    establishments_features_data: list
        A list of lists, each containing data from one of the fields in the csv file.

    Raises
    ------
    No Raises.

    Returns
    -------
    No Returns.
    """

    df_final = pd.DataFrame()

    for feature_index in range(len(establishments_features_data)):
        df_final[establishments_features_labels[feature_index]] = establishments_features_data[feature_index]

    df_final.to_csv('data/output/establishments.csv', index=False)
