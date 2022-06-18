from dotenv import load_dotenv

GOOGLE_MAPS_API = 'https://maps.googleapis.com/maps/api'
API = '/place'
SEARCH_COMPONENT = '/nearbysearch'
OUTPUT_TYPE = '/json?'

RADIUS = 3000
NORTHEAST_LAT = -25.350687
NORTHEAST_LON = -49.183989
SOUTHWEST_LAT = -25.635117
SOUTHWEST_LON = -49.380144

load_dotenv('.env')