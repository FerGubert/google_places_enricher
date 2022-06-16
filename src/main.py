from flows import calculate_coordinates, request_google_places
from config import *
import argparse

def main():
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

    if args.flow == 'coordinates':
        if all(env_vars):
            print(calculate_coordinates())
        else:
            print('[ERROR] Invalid environment variables.')
    elif args.flow == 'request':
        if RADIUS != 0:
            #request_google_places()
            print('OK')
        else:
            print('[ERROR] Invalid environment variable.')
    else:
        # erro
        pass


