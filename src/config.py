from dotenv import load_dotenv

GOOGLE_MAPS_API = 'https://maps.googleapis.com/maps/api'
API = '/place'
SEARCH_COMPONENT = '/nearbysearch'
OUTPUT_TYPE = '/json?'

RADIUS = 0
NORTHEAST_LAT = 0
NORTHEAST_LON = 0
SOUTHWEST_LAT = 0
SOUTHWEST_LON = 0

load_dotenv('.env')