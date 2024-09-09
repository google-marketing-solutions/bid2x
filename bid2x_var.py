from bid2x_application import bid2x_application

# Defaults for bid2x.  Many will be replaced
# with an deployment-specific values through
# environment variable, command line arguments
# or config file.

# Define action variable defaults.
ACTION_LIST_ALGOS = False
ACTION_LIST_SCRIPTS = False
ACTION_CREATE_ALGORITHM = False
ACTION_UPDATE_SPREADSHEET = False
ACTION_REMOVE_ALGORITHM = False
ACTION_UPDATE_SCRIPTS = False
ACTION_TEST = False

# Overall application debug flag.
DEBUG = False

# Bid2X for DV - specific defaults
CLEAR_ONOFF = False
DEFER_PATTERN = False
ALTERNATE_ALGORITHM = False

NEW_ALGO_NAME = 'bid2x'
NEW_ALGO_DISPLAY_NAME = 'bid2x'
LINE_ITEM_NAME_PATTERN = 'bid-to-x'
JSON_AUTH_FILE = 'client-secret.json'
CB_TMP_FILE_PREFIX = '/tmp/cb_script'
CB_LAST_UPDATE_FILE_PREFIX = 'last_upload'
SERVICE_ACCOUNT_EMAIL = 'gmp-bid-to-x@client-gcp.iam.gserviceaccount.com'

PARTNER_ID = 100000
ADVERTISER_ID = 100000
CB_ALGO_ID = 1000000
FLOODLIGHT_ID_LIST = [1000001,1000002]
ATTR_MODEL_ID = 0

ZONES_TO_PROCESS = "z1,z2,z3,z4,z5"

# Define Spreadsheet-specific defaults.
SPREADSHEET_KEY = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqr'
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/' + \
                              SPREADSHEET_KEY + '/edit'
# These are the columns of the default setup in the spreadsheet.
COLUMN_STATUS = 'A'
COLUMN_LINEITEMID = 'B'
COLUMN_LINEITEMNAME = 'C'
COLUMN_LINEITEMTYPE = 'D'
COLUMN_CAMPAIGNID = 'E'
COLUMN_ADVERTISERID = 'F'
COLUMN_CUSTOMBIDDING = 'K'

API_SCOPES = [
  'https://www.googleapis.com/auth/display-video',
  'https://www.googleapis.com/auth/spreadsheets']
API_NAME = 'displayvideo'
API_VERSION = 'v3'

# Variables that have specific values that cannot be
# set through options
HTTP_RETRY_TIMEOUT = 5
LARGE_PAGE_SIZE = 200
SPREADSHEET_FIRST_DATA_ROW = 2
SPREADSHEET_LAST_DATA_ROW = 1000
# Set defaults for bidding factor high and low to 1000 as top-end
# and low as 0.5 to keep values entered in associated spreadsheet
# within a 'sane' range. These values used in a min(max()) wrap
# later on in the code.
BIDDING_FACTOR_HIGH = 1000.0
BIDDING_FACTOR_LOW = 0.5


def assign_vars_to_objects (app: bid2x_application) -> None:
  app.trix = SPREADSHEET_URL
  app.scopes = API_SCOPES
  app.dv_api_name = API_NAME
  app.dv_api_version = API_VERSION

  app.action_list_algos = ACTION_LIST_ALGOS
  app.action_list_scripts = ACTION_LIST_SCRIPTS
  app.action_create_algorithm = ACTION_CREATE_ALGORITHM
  app.action_update_spreadsheet = ACTION_UPDATE_SPREADSHEET
  app.action_remove_algorithm = ACTION_REMOVE_ALGORITHM
  app.action_update_scripts = ACTION_UPDATE_SCRIPTS
  app.action_test = ACTION_TEST

  app.debug = DEBUG
  app.sheet.debug = DEBUG
  app.clear_onoff = CLEAR_ONOFF
  app.sheet.clear_onoff = CLEAR_ONOFF
  app.defer_pattern = DEFER_PATTERN
  app.alternate_algorithm = ALTERNATE_ALGORITHM
  app.new_algo_name = NEW_ALGO_NAME
  app.new_algo_display_name = NEW_ALGO_DISPLAY_NAME
  app.line_item_name_pattern = LINE_ITEM_NAME_PATTERN
  app.json_auth_file = JSON_AUTH_FILE
  app.cb_tmp_file_prefix = CB_TMP_FILE_PREFIX
  app.cb_last_update_file_prefix = CB_LAST_UPDATE_FILE_PREFIX
  app.partner_id = PARTNER_ID
  app.advertiser_id = ADVERTISER_ID
  app.cb_algo_id = CB_ALGO_ID
  app.service_account_email = SERVICE_ACCOUNT_EMAIL
  app.zones_to_process = ZONES_TO_PROCESS
  app.floodlight_id_list = FLOODLIGHT_ID_LIST
  app.attr_model_id = ATTR_MODEL_ID
  app.bidding_factor_high = BIDDING_FACTOR_HIGH
  app.bidding_factor_low = BIDDING_FACTOR_LOW
