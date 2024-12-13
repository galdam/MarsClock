import json
ROOT_PATH = f"{__file__.rsplit('/', 1)[0]}/../"
RESOURCE_PATH = f'{ROOT_PATH}/resources'

try:
    _config_obj_ = json.load(open(f'{RESOURCE_PATH}/config.json'))
except OSError as err:
    _config_obj_ = dict()

EARTH_DST_MODE = _config_obj_.get('EARTH_DST_MODE', "BST")
EARTH_TIMEZONE = _config_obj_.get('EARTH_TIMEZONE', "GMT")
EARTH_LOCATION_NAME = _config_obj_.get('EARTH_LOCATION', 'Cambridge, UK')

MARS_DATETIME_LOCALE = _config_obj_.get('MARS_DATETIME_LOCALE', 'mars.darian')
EARTH_DATETIME_LOCALE = _config_obj_.get('EARTH_DATETIME_LOCALE', 'earth.gregorian')


