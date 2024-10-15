"""
This module provides default values for all bid2x variables.

It includes function for:

- Assigning variables to objects

"""
from bid2x_application import bid2x_application
from enum import Enum

class PlatformType(Enum):
    """Platforms used for custom scripting and referencing
    such as the Google Sheet"""
    GTM = 'GTM'
    DV = 'DV'
    SHEETS = 'SHEETS'

class GTMColumns(Enum):
    ORIGIN = 'LEG_SCHD_ORIG'
    DESTINATION = 'LEG_SCHD_DEST'
    SERVER_NAME = 'CMCL_SERV_NAME'
    INDEX_FACTOR = 'INDEX_FACTOR'
    INDEX_LOW = 'INDEX_LOW'
    INDEX_HIGH = 'INDEX_HIGH'
    VALUE_ADJUSTMENT = 'VALUE_ADJUSTMENT'


# Defaults for bid2x.  Many will be replaced
# with an deployment-specific values through
# environment variable, command line arguments
# or config file.

# Overall application debug flag.
# DEBUG = False
DEBUG = True

# Platform Type using Bid2X (GTM, DV360, Ads?)
PLATFORM_TYPE = None
JSON_AUTH_FILE = 'client-secret.json'
SERVICE_ACCOUNT_EMAIL = 'gmp-bid-to-x@client-gcp.iam.gserviceaccount.com'

# GTM variables
GTM_ACCOUNT_ID = 99999999
GTM_CONTAINER_ID = 888888888
GTM_WORKSPACE_ID = 1
GTM_VARIABLE_ID = 1
GTM_INDEX_FILENAME = 'Test'
GTM_INDEX_TAB = 'index_file'
GTM_VALUE_ADJUSTMENT_TAB = 'value_adjustment'

# DV360 variables
# Define action variable defaults.
ACTION_LIST_ALGOS = False
ACTION_LIST_SCRIPTS = False
ACTION_CREATE_ALGORITHM = False
ACTION_UPDATE_SPREADSHEET = False
ACTION_REMOVE_ALGORITHM = False
ACTION_UPDATE_SCRIPTS = False
ACTION_TEST = False

# Bid2X for DV - specific defaults
CLEAR_ONOFF = False
DEFER_PATTERN = False
ALTERNATE_ALGORITHM = False

NEW_ALGO_NAME = 'bid2x'
NEW_ALGO_DISPLAY_NAME = 'bid2x'
LINE_ITEM_NAME_PATTERN = 'bid-to-x'
# JSON_AUTH_FILE = 'client-secret.json'
CB_TMP_FILE_PREFIX = '/tmp/cb_script'
CB_LAST_UPDATE_FILE_PREFIX = 'last_upload'
# SERVICE_ACCOUNT_EMAIL = 'gmp-bid-to-x@client-gcp.iam.gserviceaccount.com'


PARTNER_ID = 100000
ADVERTISER_ID = 100000
CB_ALGO_ID = 1000000
FLOODLIGHT_ID_LIST = [1000001,1000002]
ATTR_MODEL_ID = 0

ZONES_TO_PROCESS = "c1,c2,c3,c4,c5"

INPUT_FILE = None

# Define Spreadsheet-specific defaults.
SPREADSHEET_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH'
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

# Definitions for Sheets tab with updates on scripts.
DEFAULT_CB_SCRIPT_COL_UPDATE = 2
DEFAULT_CB_SCRIPT_COL_TEST = 4

# Defaults for bid2x Model's within App Object.
DEFAULT_MODEL_CAMPAIGN_ID = 10000000
DEFAULT_MODEL_ALGORITHM_ID = 1000000
DEFAULT_MODEL_SHEET_ROW = 1

# API defaults for this solution.
API_SCOPES = [
    'https://www.googleapis.com/auth/tagmanager.edit.containerversions',
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.publish',
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.delete.containers',
    'https://www.googleapis.com/auth/spreadsheets']
API_NAME = 'tagmanager'
API_VERSION = 'v2'


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
    """This function copies values from the bid2x_var scope into their
    proper places within the app object.  This function is needed to initialize
    the app object with good values before a config file load or whenever the
    app object is potentially in a state with unknown values.
    Args:
        app: a bid2x_application object - there is usually only one.
    Returns:
        None - this is a utility subroutine, not as much a function.
    """
    # Check if the 'sheet' property has been initialized and exists.
    if hasattr(app,'sheet'):
        app.sheet.sheet_id = SPREADSHEET_KEY
        app.sheet.sheet_url = \
            f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_KEY}/edit'
        app.sheet.debug = DEBUG

    # Platform type for Bid2X instance
    app.platform_type = PLATFORM_TYPE

    # DV360 connection-related properties
    app.scopes = API_SCOPES
    app.api_name = API_NAME
    app.api_version = API_VERSION

    app.debug = DEBUG
    app.platform_object.debug = DEBUG
    app.json_auth_file = JSON_AUTH_FILE
    app.service_account_email = SERVICE_ACCOUNT_EMAIL

    if app.platform_type == PlatformType.GTM:
      # GTM related properties
      app.platform_object.gtm_account_id = GTM_ACCOUNT_ID
      app.platform_object.gtm_container_id = GTM_CONTAINER_ID
      app.platform_object.gtm_workspace_id = GTM_WORKSPACE_ID
      app.platform_object.gtm_variable_id = GTM_VARIABLE_ID

    if app.platform_type == PlatformType.DV:
      # Initialize action-related properties
      app.platform_object.action_list_algos = bool(ACTION_LIST_ALGOS)
      app.platform_object.action_list_scripts = bool(ACTION_LIST_SCRIPTS)
      app.platform_object.action_create_algorithm = bool(ACTION_CREATE_ALGORITHM)
      app.platform_object.action_update_spreadsheet = bool(ACTION_UPDATE_SPREADSHEET)
      app.platform_object.action_remove_algorithm = bool(ACTION_REMOVE_ALGORITHM)
      app.platform_object.action_update_scripts = bool(ACTION_UPDATE_SCRIPTS)
      app.platform_object.action_test = bool(ACTION_TEST)

      # Initialize all the rest of the properties
      app.platform_object.clear_onoff = CLEAR_ONOFF
      app.sheet.clear_onoff = CLEAR_ONOFF
      app.platform_object.defer_pattern = DEFER_PATTERN
      app.platform_object.alternate_algorithm = ALTERNATE_ALGORITHM
      app.platform_object.new_algo_name = NEW_ALGO_NAME
      app.platform_object.new_algo_display_name = NEW_ALGO_DISPLAY_NAME
      app.platform_object.line_item_name_pattern = LINE_ITEM_NAME_PATTERN
      app.platform_object.cb_tmp_file_prefix = CB_TMP_FILE_PREFIX
      app.platform_object.cb_last_update_file_prefix = CB_LAST_UPDATE_FILE_PREFIX
      app.platform_object.partner_id = PARTNER_ID
      app.platform_object.advertiser_id = ADVERTISER_ID
      app.platform_object.cb_algo_id = CB_ALGO_ID
      app.platform_object.zones_to_process = ZONES_TO_PROCESS
      app.platform_object.floodlight_id_list = FLOODLIGHT_ID_LIST
      app.platform_object.attr_model_id = ATTR_MODEL_ID
      app.platform_object.bidding_factor_high = BIDDING_FACTOR_HIGH
      app.platform_object.bidding_factor_low = BIDDING_FACTOR_LOW
