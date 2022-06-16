import requests
import json
import pandas as pd

def initialize_variables():
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

def make_request(url, params={}):
    res = requests.get(url, params = params)
    results = json.loads(res.content)
    return results

def export_data(establishments_features_labels, establishments_features_data):
    df_final = pd.DataFrame()

    for feature_index in range(len(establishments_features_data)):
        df_final[establishments_features_labels[feature_index]] = establishments_features_data[feature_index]

    df_final.to_csv('../data/output/establishments.csv', index=False)