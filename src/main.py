from flows import calculate_coordinates, request_google_places
from config import *
import argparse

from src.flows import match_category_phrases

def main():
    """
    Retrieve the argument passed by the user.

    Parameters
    ----------
    No Parameters.

    Raises
    ------
    No Raises.

    Returns
    -------
    argparse.ArgumentParser
        Argument name and the content passed by the user.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--flow', dest='flow')
    args = parser.parse_args()

    return args

if __name__== "__main__" :
    
    args = main()

    env_vars = [RADIUS,
                NORTHEAST_LAT,
                NORTHEAST_LON,
                SOUTHWEST_LAT,
                SOUTHWEST_LON]

    if (args.flow == 'coordinates') and (all(env_vars)):
        print(calculate_coordinates())
    elif (args.flow == 'request') and (RADIUS != 0):
        print(request_google_places())
    elif args.flow == 'match':
        print(match_category_phrases())
    else:
        print('[ERROR] Invalid environment variables or invalid argument.')


