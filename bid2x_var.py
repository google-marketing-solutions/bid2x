"""BidToX - bid2x_var application module.

  Copyright 2025 Google Inc.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Description:
  ------------

  This module provides default values for all bid2x variables.
"""

import enum

Enum = enum.Enum


class PlatformType(Enum):
  """Platforms used for custom scripting and referencing."""
  GTM = 'GTM'
  DV = 'DV'
  SHEETS = 'SHEETS'


class GTMColumns(Enum):
  GTM_VAR_1 = 'VARIABLE-ONE'
  GTM_VAR_2 = 'VARIABLE-TWO'
  GTM_NORMAL_TOTAL = 'Pixel-Transaction-TotalCAD'
  SERVER_NAME = 'CMCL_SERV_NAME'
  INDEX_FACTOR = 'INDEX_FACTOR'
  INDEX_LOW = 'INDEX_LOW'
  INDEX_HIGH = 'INDEX_HIGH'
  VALUE_ADJUSTMENT = 'VALUE_ADJUSTMENT'


# Defaults for bid2x.  Many will be replaced
# with deployment-specific values through
# command line arguments or config file.

# Overall application debug flag.
TRACE = True
DEBUG = True

# Platform Type using Bid2X (GTM, DV360, Ads?)
PLATFORM_TYPE = 'DV'  # Default platform type is DV.
JSON_AUTH_FILE = 'client-secret.json'
SERVICE_ACCOUNT_EMAIL = 'gmp-bid-to-x@client-gcp.iam.gserviceaccount.com'

# GTM variables
GTM_ACCOUNT_ID = 90000000
GTM_CONTAINER_ID = 800000000
GTM_WORKSPACE_ID = 100
GTM_VARIABLE_ID = 0
GTM_INDEX_FILENAME = 'Test'
GTM_INDEX_TAB = 'index_file'
GTM_VALUE_ADJUSTMENT_TAB = 'value_adjustment'
GTM_STATUS_TAB = 'JS_Scripts'

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
JSON_AUTH_FILE = 'client-secret.json'
CB_TMP_FILE_PREFIX = '/tmp/cb_script'
CB_LAST_UPDATE_FILE_PREFIX = 'last_upload'
SERVICE_ACCOUNT_EMAIL = 'bid-to-x@client-gcp.iam.gserviceaccount.com'
DV_STATUS_TAB = 'CB_Scripts'

PARTNER_ID = 100000
ADVERTISER_ID = 100000
CB_ALGO_ID = 1000000
FLOODLIGHT_ID_LIST = '1000001,1000002'
ATTR_MODEL_ID = 0

ZONES_TO_PROCESS = 'c1,c2,c3,c4,c5'

INPUT_FILE = None

# Define Spreadsheet-specific defaults.
SPREADSHEET_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGH'
SPREADSHEET_URL = (
    'https://docs.google.com/spreadsheets/d/' + SPREADSHEET_KEY + '/edit'
)
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
    'https://www.googleapis.com/auth/display-video',
    'https://www.googleapis.com/auth/spreadsheets',
]
API_NAME = 'displayvideo'
API_VERSION = 'v3'

GTM_API_SCOPES = [
    'https://www.googleapis.com/auth/tagmanager.edit.containerversions',
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.publish',
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.delete.containers',
    'https://www.googleapis.com/auth/spreadsheets']
GTM_API_NAME = 'tagmanager'
GTM_API_VERSION = 'v2'


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


