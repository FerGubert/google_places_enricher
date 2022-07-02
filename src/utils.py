from config import *
import requests
import json
import pandas as pd
import os
import re
from sentence_transformers import SentenceTransformer, util

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

def initialize_variables_request():
    """
    Initializes the main variables used in the Google places API request.

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
    vicinity,category = ([] for i in range(11))

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

def create_url_request(lat, lon, cat):
    """
    Creates the url that will be used to make the request to the Google places API.

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
        Url for the request in the Google places API.
    """

    location = '&location={:s},{:s}'.format(str(lat), str(lon))
    radius = '&radius={:s}'.format(str(RADIUS))
    establishment_keyword = '&keyword={:s}'.format(cat)
    api_key = '&key={:s}'.format(os.getenv('KEY'))

    return GOOGLE_MAPS_API + API + SEARCH_COMPONENT + OUTPUT_TYPE + api_key + location + radius + establishment_keyword

def make_request(url, params={}):
    """
    Make the request to the Google places API.

    Parameters
    ----------
    url: str
        Url for the request in the Google places API.
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

def treat_data_request(df):
    """
    Performs a treatment on the data, eliminating the json format of the location field and 
    making aggregations to keep only single establishments.

    Parameters
    ----------
    df: pandas.core.frame.DataFrame
        The data to be processed.

    Raises
    ------
    No Raises.

    Returns
    -------
    pandas.core.frame.DataFrame
        The processed data.
    """
 
    df['geometry'] = df['geometry'].astype(str)
    df_estab_cat = df.groupby('place_id')[['geometry', 'category']].agg(['unique'])

    lat = []
    lon = []
    for coordinates in df_estab_cat['geometry']['unique']:
        coordinates_numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', str(coordinates))]
        lat.append(coordinates_numbers[0])
        lon.append(coordinates_numbers[1])
    df_estab_cat['lat'] = lat
    df_estab_cat['lon'] = lon

    df_estab_cat.columns = ['_'.join(col) for col in df_estab_cat.columns]
    df_estab_cat.reset_index(inplace=True)
    df_estab_cat.rename(columns={'category_unique': 'categories', 'lat_': 'lat', 'lon_': 'lon', 'place_id_': 'place_id'}, inplace=True)

    df_place_id = df.drop_duplicates(subset="place_id")
    df_place_id.drop(columns=['geometry', 'opening_hours', 'category'], inplace=True)
    df_final = df_estab_cat.merge(df_place_id, on='place_id', how='left')
    df_final.drop(columns=['geometry_unique'], inplace=True)

    return df_final

def export_data_request(establishments_features_labels, establishments_features_data):
    """
    Create dataframe, performs data processing and save data in csv file.

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

    df_raw = pd.DataFrame()
    for feature_index in range(len(establishments_features_data)):
        df_raw[establishments_features_labels[feature_index]] = establishments_features_data[feature_index]

    df_trusted = treat_data_request(df_raw)
    df_trusted.to_csv('data/output/establishments.csv', index=False)

def delete_cat_google(categories_google):
    """
    Remove Google categories that don't add value.

    Parameters
    ----------
    categories_google: list
        A list of all Google categories referring to an establishment.

    Raises
    ------
    No Raises.

    Returns
    -------
    list
        The list with only the Google categories of interest.
    """

    new_cat_google = []
    for category in categories_google:
        if(category == 'point_of_interest') or (category == 'establishment'):
            continue
        else:
            new_cat_google.append(category)

    return new_cat_google

def convert_string_to_list(text, sep):
    """
    Treat the text, separate the words and convert to list.

    Parameters
    ----------
    text: str
        The text to be converted to list.
    sep: str
        The separator to use to separate the words.

    Raises
    ------
    No Raises.

    Returns
    -------
    list
        The list with the words of the text.
    """

    list_final = []
    items = text.split(sep)
    for item in items:
        item = item.replace('\'', '').replace('[', '').replace(']', '').strip()
        list_final.append(item)
    return list_final

def create_yelp_phrase(df_categories_yelp):
    """
    Creates the yelp phrase joining the 4 hierarchical levels of the categories.

    Parameters
    ----------
    df_categories_yelp: pandas.core.frame.DataFrame
        Yelp data with 4 hierarchical levels.

    Raises
    ------
    No Raises.

    Returns
    -------
    pandas.core.series.Series
        The treated Yelp phrases.
    """

    df_categories_yelp['phrase_yelp'] = df_categories_yelp[['parent_1', 'parent_2', 'parent_3', 'leaf']]\
                                    .apply(' '.join, axis=1)
    yelp_phrases = df_categories_yelp['phrase_yelp'].apply(lambda phrase: phrase\
                                    .replace(' - ', ' ').replace('- ', '').replace(',', ''))

    return yelp_phrases

def create_estab_phrase(df_estab):
    """
    Creates the phrases of the establishments from the Google categories and the enrichment categories. 
    Each enrichment category is merged with all the Google categories of that establishment.

    Parameters
    ----------
    df_estab: pandas.core.frame.DataFrame
        The property data obtained from the Google places API.

    Raises
    ------
    No Raises.

    Returns
    -------
    pandas.core.frame.DataFrame
        The phrases of the establishments with their respective ID.
    """

    df_categories_estab = df_estab[['place_id', 'categories', 'types']]
    df_categories_estab['types_list'] = df_categories_estab['types'].apply(lambda types: convert_string_to_list(types, ','))
    df_categories_estab['categories_google'] = df_categories_estab['types_list'].apply(lambda types_list: delete_cat_google(types_list))
    df_categories_estab['categories_enrichment'] = df_categories_estab['categories'].apply(lambda categories: convert_string_to_list(categories, '\' '))

    place_id = []
    phrase_list = []

    for row in df_categories_estab.iterrows():
        for cat_enrich in row[1]['categories_enrichment']:
            phrase = cat_enrich
            for cat_google in row[1]['categories_google']:
                phrase = phrase + ' ' + cat_google
            place_id.append(row[1]['place_id'])
            phrase_list.append(phrase)
    
    df_categories_estab_phrases = pd.DataFrame()
    df_categories_estab_phrases['place_id'] = place_id
    df_categories_estab_phrases['phrase_establishment'] = phrase_list
    df_categories_estab_phrases['phrase_establishment'] = df_categories_estab_phrases['phrase_establishment'].apply(lambda phrase: phrase.replace(',', ''))

    return df_categories_estab_phrases

def calculate_similarity_sentences(sentences_estab, sentences_yelp):
    """
    Calculates the semantic textual similarity between the Yelp sentences and the establishments sentences, 
    using a Sentence Transformer model to generate the embeddings and the cosine similarity to calculate the distance between the vectors.
    And retrieves for each establishment sentence, the Yelp sentence with the highest score.

    Parameters
    ----------
    sentences_estab: pandas.core.series.Series
        The establishments sentences.
    sentences_yelp: pandas.core.series.Series
        The Yelp sentences.

    Raises
    ------
    No Raises.

    Returns
    -------
    pandas.core.frame.DataFrame
        The establishments sentences combined with the best-scoring Yelp sentences.
    """

    model = SentenceTransformer('all-MiniLM-L6-v2')

    embeddings_estab = model.encode(sentences_estab, convert_to_tensor=True)
    embeddings_yelp = model.encode(sentences_yelp, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings_estab, embeddings_yelp)

    rows = len(sentences_estab)
    columns = len(sentences_yelp)
    pairs_final = []
    for i in range(rows):
        pairs = []
        for j in range(columns):
            pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})
        pairs_final.append(pairs)

    best_scores = []
    for pairs in pairs_final:
        pairs = sorted(pairs, key=lambda x: x['score'], reverse=True)
        best_scores.append(pairs[0])

    phrase_estab = []
    phrase_yelp = []
    score = []
    for pair in best_scores:
        i, j = pair['index']
        phrase_estab.append(sentences_estab[i])
        phrase_yelp.append(sentences_yelp[j])
        score.append(round(float(pair['score']), 4))

    df_score = pd.DataFrame()
    df_score['phrase_establishment'] = phrase_estab
    df_score['phrase_yelp'] = phrase_yelp
    df_score['score'] = score

    return df_score