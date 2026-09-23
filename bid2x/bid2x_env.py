"""BidToX - bid2x_env tool.

  Copyright 2025 Google LLC

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Description:
  ------------

  This code helps with the ingestion of bid2x variables when it is being stored
  in environment variables.
"""

import os

import bid2x_var

_TRUTHY = frozenset({'y', 'yes', 't', 'true', 'on', '1'})
_FALSY = frozenset({'n', 'no', 'f', 'false', 'off', '0'})


def parse_bool(value: str | bool) -> bool:
  """Parse a string or bool into a bool.

  Accepts the same truthy/falsy tokens as the former distutils strtobool
  helper, but returns a bool instead of 0 or 1.

  Args:
    value: Environment string or bool default to parse.

  Returns:
    Parsed boolean value.

  Raises:
    ValueError: If the string is not a recognized boolean token.
  """
  if isinstance(value, bool):
    return value

  normalized = value.strip().lower()
  if normalized in _TRUTHY:
    return True
  if normalized in _FALSY:
    return False
  raise ValueError(f'invalid truth value {value!r}')


def _env_bool(name: str, default: bool) -> bool:
  value = os.getenv(name)
  if value is None:
    return default
  return parse_bool(value)


def process_environment_vars() -> None:
  """Load bid2x configuration values from environment variables."""

  # Extract run-time parameters from environment variables setting a default
  # when the parameter doesn't exist.  The default value, when the environment
  # variable does not exist is just the same variable name from the
  # bid2x_var scope.  This keeps the default value in one place in the
  # project.

  # Read in action environment variables.
  bid2x_var.ACTION_LIST_ALGOS = _env_bool(
      'ACTION_LIST_ALGOS', bid2x_var.ACTION_LIST_ALGOS)
  bid2x_var.ACTION_LIST_SCRIPTS = _env_bool(
      'ACTION_LIST_SCRIPTS', bid2x_var.ACTION_LIST_SCRIPTS)
  bid2x_var.ACTION_CREATE_ALGORITHM = _env_bool(
      'ACTION_CREATE_ALGORITHM', bid2x_var.ACTION_CREATE_ALGORITHM)
  bid2x_var.ACTION_UPDATE_SPREADSHEET = _env_bool(
      'ACTION_UPDATE_SPREADSHEET', bid2x_var.ACTION_UPDATE_SPREADSHEET)
  bid2x_var.ACTION_REMOVE_ALGORITHM = _env_bool(
      'ACTION_REMOVE_ALGORITHM', bid2x_var.ACTION_REMOVE_ALGORITHM)
  bid2x_var.ACTION_UPDATE_SCRIPTS = _env_bool(
      'ACTION_UPDATE_SCRIPTS', bid2x_var.ACTION_UPDATE_SCRIPTS)
  bid2x_var.ACTION_TEST = _env_bool('ACTION_TEST', bid2x_var.ACTION_TEST)

  # Read in Boolean environment variables.
  bid2x_var.DEBUG = _env_bool('DEBUG', bid2x_var.DEBUG)
  bid2x_var.CLEAR_ONOFF = _env_bool('CLEAR_ONOFF', bid2x_var.CLEAR_ONOFF)
  bid2x_var.DEFER_PATTERN = _env_bool(
      'DEFER_PATTERN', bid2x_var.DEFER_PATTERN)
  bid2x_var.ALTERNATE_ALGORITHM = _env_bool(
      'ALTERNATE_ALGORITHM', bid2x_var.ALTERNATE_ALGORITHM)

  # Read in Bid2x --> DV360 related environment variables.
  bid2x_var.NEW_ALGO_NAME = os.getenv(
      'NEW_ALGO_NAME', bid2x_var.NEW_ALGO_NAME)
  bid2x_var.NEW_ALGO_DISPLAY_NAME = os.getenv(
      'NEW_ALGO_DISPLAY_NAME', bid2x_var.NEW_ALGO_DISPLAY_NAME)
  bid2x_var.LINE_ITEM_NAME_PATTERN = os.getenv(
      'LINE_ITEM_NAME_PATTERN', bid2x_var.LINE_ITEM_NAME_PATTERN)
  bid2x_var.JSON_AUTH_FILE = os.getenv(
      'JSON_AUTH_FILE', bid2x_var.JSON_AUTH_FILE)
  bid2x_var.CB_TMP_FILE_PREFIX = os.getenv(
      'CB_TMP_FILE_PREFIX', bid2x_var.CB_TMP_FILE_PREFIX)
  bid2x_var.CB_LAST_UPDATE_FILE_PREFIX = os.getenv(
      'CB_LAST_UPDATE_FILE_PREFIX', bid2x_var.CB_LAST_UPDATE_FILE_PREFIX)
  bid2x_var.PARTNER_ID = int(os.getenv(
      'PARTNER_ID', bid2x_var.PARTNER_ID))
  bid2x_var.ADVERTISER_ID = int(os.getenv(
      'ADVERTISER_ID', bid2x_var.ADVERTISER_ID))
  bid2x_var.CB_ALGO_ID = int(os.getenv(
      'CB_ALGO_ID', bid2x_var.CB_ALGO_ID))
  bid2x_var.SERVICE_ACCOUNT_EMAIL = os.getenv(
      'SERVICE_ACCOUNT_EMAIL', bid2x_var.SERVICE_ACCOUNT_EMAIL)
  bid2x_var.ZONES_TO_PROCESS = os.getenv(
      'ZONES_TO_PROCESS', bid2x_var.ZONES_TO_PROCESS)
  bid2x_var.FLOODLIGHT_ID_LIST = os.getenv(
      'FLOODLIGHT_ID_LIST', bid2x_var.FLOODLIGHT_ID_LIST)
  bid2x_var.ATTR_MODEL_ID = int(os.getenv(
      'ATTR_MODEL_ID', bid2x_var.ATTR_MODEL_ID))
  bid2x_var.BIDDING_FACTOR_HIGH = float(os.getenv(
      'BIDDING_FACTOR_HIGH', bid2x_var.BIDDING_FACTOR_HIGH))
  bid2x_var.BIDDING_FACTOR_LOW = float(os.getenv(
      'BIDDING_FACTOR_LOW', bid2x_var.BIDDING_FACTOR_LOW))

  # Read in spreadsheet-related environment variables.
  bid2x_var.SPREADSHEET_KEY = os.getenv(
      'SPREADSHEET_KEY', bid2x_var.SPREADSHEET_KEY)
  bid2x_var.SPREADSHEET_URL = os.getenv(
      'SPREADSHEET_URL', bid2x_var.SPREADSHEET_URL)
  bid2x_var.COLUMN_STATUS = os.getenv(
      'COLUMN_STATUS', bid2x_var.COLUMN_STATUS)
  bid2x_var.COLUMN_LINEITEMID = os.getenv(
      'COLUMN_LINEITEMID', bid2x_var.COLUMN_LINEITEMID)
  bid2x_var.COLUMN_LINEITEMNAME = os.getenv(
      'COLUMN_LINEITEMNAME', bid2x_var.COLUMN_LINEITEMNAME)
  bid2x_var.COLUMN_LINEITEMTYPE = os.getenv(
      'COLUMN_LINEITEMTYPE', bid2x_var.COLUMN_LINEITEMTYPE)
  bid2x_var.COLUMN_CAMPAIGNID = os.getenv(
      'COLUMN_CAMPAIGNID', bid2x_var.COLUMN_CAMPAIGNID)
  bid2x_var.COLUMN_ADVERTISERID = os.getenv(
      'COLUMN_ADVERTISERID', bid2x_var.COLUMN_ADVERTISERID)
  bid2x_var.COLUMN_CUSTOMBIDDING = os.getenv(
      'COLUMN_CUSTOMBIDDING', bid2x_var.COLUMN_CUSTOMBIDDING)

  bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE = os.getenv(
      'DEFAULT_CB_SCRIPT_COL_UPDATE', bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE)
  bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST = os.getenv(
      'DEFAULT_CB_SCRIPT_COL_TEST', bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST)
