import os
from distutils.util import strtobool
import bid2x_var

def process_environment_vars() -> None:

  # Extract run-time parameters from environment variables setting a default
  # when the parameter doesn't exist.  The default value, when the environment
  # variable does not exist is just the same variable name from the
  # bid2x_var scope.  This keeps the default value in one place in the
  # project.

  # Read in action environment variables.
  bid2x_var.ACTION_LIST_ALGOS = strtobool(
    os.getenv('ACTION_LIST_ALGOS',bid2x_var.ACTION_LIST_ALGOS))
  bid2x_var.ACTION_LIST_SCRIPTS = strtobool(
    os.getenv('ACTION_LIST_SCRIPTS',bid2x_var.ACTION_LIST_SCRIPTS))
  bid2x_var.ACTION_CREATE_ALGORITHM = strtobool(
    os.getenv('ACTION_CREATE_ALGORITHM',bid2x_var.ACTION_CREATE_ALGORITHM))
  bid2x_var.ACTION_UPDATE_SPREADSHEET = strtobool(
    os.getenv('ACTION_UPDATE_SPREADSHEET',bid2x_var.ACTION_UPDATE_SPREADSHEET))
  bid2x_var.ACTION_REMOVE_ALGORITHM = strtobool(
    os.getenv('ACTION_REMOVE_ALGORITHM',bid2x_var.ACTION_REMOVE_ALGORITHM))
  bid2x_var.ACTION_UPDATE_SCRIPTS = strtobool(
    os.getenv('ACTION_UPDATE_SCRIPTS',bid2x_var.ACTION_UPDATE_SCRIPTS))
  bid2x_var.ACTION_TEST = strtobool(
    os.getenv('ACTION_TEST',bid2x_var.ACTION_TEST))

  # Read in Boolean environment variables.
  bid2x_var.DEBUG = strtobool(
    os.getenv('DEBUG',bid2x_var.DEBUG))
  bid2x_var.CLEAR_ONOFF = strtobool(
    os.getenv('CLEAR_ONOFF',bid2x_var.CLEAR_ONOFF))
  bid2x_var.DEFER_PATTERN = strtobool(
    os.getenv('DEFER_PATTERN',bid2x_var.DEFER_PATTERN))
  bid2x_var.ALTERNATE_ALGORITHM = strtobool(
    os.getenv('ALTERNATE_ALGORITHM',bid2x_var.ALTERNATE_ALGORITHM))

  # Read in Bid2x --> DV360 related environment variables.
  bid2x_var.NEW_ALGO_NAME = os.getenv(
    'NEW_ALGO_NAME',bid2x_var.NEW_ALGO_NAME)
  bid2x_var.NEW_ALGO_DISPLAY_NAME = os.getenv(
    'NEW_ALGO_DISPLAY_NAME',bid2x_var.NEW_ALGO_DISPLAY_NAME)
  bid2x_var.LINE_ITEM_NAME_PATTERN = os.getenv(
    'LINE_ITEM_NAME_PATTERN',bid2x_var.LINE_ITEM_NAME_PATTERN)
  bid2x_var.JSON_AUTH_FILE = os.getenv(
    'JSON_AUTH_FILE',bid2x_var.JSON_AUTH_FILE)
  bid2x_var.CB_TMP_FILE_PREFIX = os.getenv(
    'CB_TMP_FILE_PREFIX',bid2x_var.CB_TMP_FILE_PREFIX)
  bid2x_var.CB_LAST_UPDATE_FILE_PREFIX = os.getenv(
    'CB_LAST_UPDATE_FILE_PREFIX',bid2x_var.CB_LAST_UPDATE_FILE_PREFIX)
  bid2x_var.PARTNER_ID = int(os.getenv(
    'PARTNER_ID',bid2x_var.PARTNER_ID))
  bid2x_var.ADVERTISER_ID = int(os.getenv(
    'ADVERTISER_ID',bid2x_var.ADVERTISER_ID))
  bid2x_var.CB_ALGO_ID = int(os.getenv(
    'CB_ALGO_ID',bid2x_var.CB_ALGO_ID))
  bid2x_var.SERVICE_ACCOUNT_EMAIL = os.getenv(
    'SERVICE_ACCOUNT_EMAIL',bid2x_var.SERVICE_ACCOUNT_EMAIL)
  bid2x_var.ZONES_TO_PROCESS = os.getenv(
    'ZONES_TO_PROCESS',bid2x_var.ZONES_TO_PROCESS)
  bid2x_var.FLOODLIGHT_ID_LIST = os.getenv(
    'FLOODLIGHT_ID_LIST',bid2x_var.FLOODLIGHT_ID_LIST)
  bid2x_var.ATTR_MODEL_ID = int(os.getenv(
    'ATTR_MODEL_ID',bid2x_var.ATTR_MODEL_ID))
  bid2x_var.BIDDING_FACTOR_HIGH = float(os.getenv(
    'BIDDING_FACTOR_HIGH',bid2x_var.BIDDING_FACTOR_HIGH))
  bid2x_var.BIDDING_FACTOR_LOW = float(os.getenv(
    'BIDDING_FACTOR_LOW',bid2x_var.BIDDING_FACTOR_LOW))

  # Read in spreadsheet-related environment variables.
  bid2x_var.SPREADSHEET_KEY = os.getenv(
    'SPREADSHEET_KEY',bid2x_var.SPREADSHEET_KEY)
  bid2x_var.SPREADSHEET_URL = os.getenv(
    'SPREADSHEET_URL', bid2x_var.SPREADSHEET_URL)
  bid2x_var.COLUMN_STATUS = os.getenv(
    'COLUMN_STATUS',bid2x_var.COLUMN_STATUS)
  bid2x_var.COLUMN_LINEITEMID = os.getenv(
    'COLUMN_LINEITEMID',bid2x_var.COLUMN_LINEITEMID)
  bid2x_var.COLUMN_LINEITEMNAME = os.getenv(
    'COLUMN_LINEITEMNAME',bid2x_var.COLUMN_LINEITEMNAME)
  bid2x_var.COLUMN_LINEITEMTYPE = os.getenv(
    'COLUMN_LINEITEMTYPE',bid2x_var.COLUMN_LINEITEMTYPE)
  bid2x_var.COLUMN_CAMPAIGNID = os.getenv(
    'COLUMN_CAMPAIGNID',bid2x_var.COLUMN_CAMPAIGNID)
  bid2x_var.COLUMN_ADVERTISERID = os.getenv(
    'COLUMN_ADVERTISERID',bid2x_var.COLUMN_ADVERTISERID)
  bid2x_var.COLUMN_CUSTOMBIDDING = os.getenv(
    'COLUMN_CUSTOMBIDDING',bid2x_var.COLUMN_CUSTOMBIDDING)

  bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE = os.getenv(
    'DEFAULT_CB_SCRIPT_COL_UPDATE',bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE)
  bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST = os.getenv(
    'DEFAULT_CB_SCRIPT_COL_TEST',bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST)
