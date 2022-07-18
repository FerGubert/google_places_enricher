from flows import calculate_coordinates, request_google_places, match_category_phrases
from config import *
import argparse

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
    parser.add_argument('--task', dest='task')
    args = parser.parse_args()

    return args

if __name__== "__main__" :
    
    args = main()

    env_vars = [RADIUS,
                NORTHEAST_LAT,
                NORTHEAST_LON,
                SOUTHWEST_LAT,
                SOUTHWEST_LON]

    if (args.task == 'coordinates') and (all(env_vars)):
        print(calculate_coordinates())
    elif (args.task == 'request') and (RADIUS != 0):
        print(request_google_places())
    elif args.task == 'match':
        print(match_category_phrases())
    else:
        print('[ERROR] Invalid environment variables or invalid argument.')


