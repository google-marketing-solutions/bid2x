"""BidToX - bid2x_application module.

  Copyright 2025 Google LLC

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

  This module contains the bid2x_application class.  This class is the
  main object that is used to run the Bid2X system.  It contains references
  to all the other objects that are used by the system and provides methods
  to run the system.
"""

import enum
import logging
from typing import Any

from auth import bid2x_auth
from bid2x_dv import Bid2xDV
from bid2x_gtm import Bid2xGTM
from bid2x_spreadsheet import Bid2xSpreadsheet
import bid2x_var
from googleapiclient import discovery

Enum = enum.Enum
Bid2xAuth = bid2x_auth.Bid2xAuth
logger = logging.getLogger(__name__)


class Bid2xApplication:
  """Main orchestrator for the Bid2X system."""

  def __init__(
      self,
      scopes: str,
      api_name: str,
      api_version: str,
      sheet_id: str,
      auth_file: str,
      platform_type: str,
  ) -> None:
    self.scopes = scopes
    self.api_name = api_name
    self.api_version = api_version
    self.service: discovery.Resource | None = None
    self.debug = False
    self.trace = False
    self.platform_type = platform_type
    self.platform_object: Bid2xDV | Bid2xGTM | None = None
    self.zone_array: list[Any] = []

    self.sheet = Bid2xSpreadsheet(sheet_id, auth_file)
    self.auth = Bid2xAuth(scopes, api_name, api_version)

  def __str__(self) -> str:
    """Return a formatted summary of application state."""
    return_str = (
        f'api_name: {self.api_name}\n'
        f'api_version: {self.api_version}\n'
        f'service: {self.service}\n'
        f'scopes: {self.scopes}\n'
        f'debug: {self.debug}\n'
        f'trace: {self.trace}\n'
        f'sheet: {self.sheet}\n'
        f'auth: {self.auth}\n'
        '---------------\n'
        'Platform Object\n'
        '---------------\n'
        f'object type: {self.platform_type}\n'
        '---------------\n'
        f'{self.platform_object}\n'
        '---------------\n'
        'Zones:\n'
    )
    for zone in self.zone_array:
      return_str += str(zone) + '\n----------------------\n'

    return return_str

  def __getstate__(self) -> dict[str, Any]:
    """Return object state without the non-serializable service attribute."""
    state = self.__dict__.copy()
    state.pop('service', None)
    return state

  def authenticate_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str | None = None,
      service_type: str | None = None,
  ) -> discovery.Resource | bool:
    """Authenticate and return the requested Google API service."""
    if service_type == bid2x_var.PlatformType.GTM.value:
      self.service = self.auth.auth_gtm_service(
          path_to_service_account_json_file, impersonation_email
      )
      return self.service

    if service_type == bid2x_var.PlatformType.DV.value:
      self.service = self.auth.auth_dv_service(
          path_to_service_account_json_file, impersonation_email
      )
      return self.service

    if service_type == bid2x_var.PlatformType.SHEETS.value:
      self.sheet.sheets_service = self.auth.auth_sheets(
          path_to_service_account_json_file, impersonation_email
      )
      logger.debug(
          'Sheets service ready for sheet_id=%s url=%s',
          self.sheet.sheet_id,
          self.sheet.sheet_url,
      )
      return self.sheet.sheets_service

    logger.error(
        'Unknown service type for authentication: %s', service_type
    )
    return False

  def start_service(self) -> None:
    """Create the platform object based on platform_type."""
    if self.platform_type == bid2x_var.PlatformType.GTM.value:
      self.platform_object = Bid2xGTM(self.sheet, self.debug)
    elif self.platform_type == bid2x_var.PlatformType.DV.value:
      self.platform_object = Bid2xDV(self.sheet, self.debug)

  def run_script(self) -> bool:
    """Run script creation and upload for the configured platform."""
    if self.debug:
      logger.debug('Platform type: %s', self.platform_type)

    if self.platform_type == bid2x_var.PlatformType.GTM.value:
      self.platform_object.process_script(self.service)
    elif self.platform_type == bid2x_var.PlatformType.DV.value:
      self.platform_object.process_script(self.service)
    else:
      return False

    return True

  def top_level_copy(self, source: dict[str, Any]) -> None:
    """Copy top-level config values from a loaded JSON config."""
    self.scopes = source['scopes']
    self.api_name = source['api_name']
    self.api_version = source['api_version']
    self.platform_type = source['platform_type']
    self.service_account_email = source['service_account_email']
    self.json_auth_file = source['json_auth_file']
    self.debug = source['debug']
    self.trace = source['trace']

    if self.platform_object is not None:
      self.platform_object.top_level_copy(source)

  def assign_vars_to_objects(self) -> None:
    """Copy default values from bid2x_var into this app and child objects."""
    if not hasattr(self, 'sheet'):
      self.sheet = Bid2xSpreadsheet(
          bid2x_var.SPREADSHEET_KEY, bid2x_var.JSON_AUTH_FILE
      )

    self.sheet.sheet_id = bid2x_var.SPREADSHEET_KEY
    self.sheet.sheet_url = (
        'https://docs.google.com/spreadsheets/d'
        f'/{bid2x_var.SPREADSHEET_KEY}/edit'
    )
    self.sheet.debug = bid2x_var.DEBUG
    self.sheet.trace = bid2x_var.TRACE

    self.platform_type = bid2x_var.PLATFORM_TYPE
    self.scopes = bid2x_var.API_SCOPES
    self.api_name = bid2x_var.API_NAME
    self.api_version = bid2x_var.API_VERSION
    self.debug = bid2x_var.DEBUG
    self.json_auth_file = bid2x_var.JSON_AUTH_FILE
    self.service_account_email = bid2x_var.SERVICE_ACCOUNT_EMAIL

    if self.platform_type == bid2x_var.PlatformType.GTM.value:
      zone_index = 1
      for zone in self.zone_array:
        zone.name = f'Zone {zone_index}'
        zone.account_id = bid2x_var.GTM_ACCOUNT_ID + zone_index
        zone.container_id = bid2x_var.GTM_CONTAINER_ID + zone_index
        zone.workspace_id = bid2x_var.GTM_WORKSPACE_ID + zone_index
        zone.variable_id = bid2x_var.GTM_VARIABLE_ID + zone_index
        zone.debug = bid2x_var.DEBUG
        zone.trace = bid2x_var.TRACE
        zone.update_row = zone_index + 1
        zone.update_col = bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE
        zone.test_row = zone_index + 1
        zone.test_col = bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST
        zone_index += 1

    if (
        self.platform_type == bid2x_var.PlatformType.DV.value
        and self.platform_object is not None
    ):
      self.platform_object.action_list_algos = bool(bid2x_var.ACTION_LIST_ALGOS)
      self.platform_object.action_list_scripts = bool(
          bid2x_var.ACTION_LIST_SCRIPTS
      )
      self.platform_object.action_create_algorithm = bool(
          bid2x_var.ACTION_CREATE_ALGORITHM
      )
      self.platform_object.action_update_spreadsheet = bool(
          bid2x_var.ACTION_UPDATE_SPREADSHEET
      )
      self.platform_object.action_remove_algorithm = bool(
          bid2x_var.ACTION_REMOVE_ALGORITHM
      )
      self.platform_object.action_update_scripts = bool(
          bid2x_var.ACTION_UPDATE_SCRIPTS
      )
      self.platform_object.action_test = bool(bid2x_var.ACTION_TEST)

      self.platform_object.clear_onoff = bid2x_var.CLEAR_ONOFF
      self.sheet.clear_onoff = bid2x_var.CLEAR_ONOFF
      self.platform_object.defer_pattern = bid2x_var.DEFER_PATTERN
      self.platform_object.alternate_algorithm = bid2x_var.ALTERNATE_ALGORITHM
      self.platform_object.new_algo_name = bid2x_var.NEW_ALGO_NAME
      self.platform_object.new_algo_display_name = (
          bid2x_var.NEW_ALGO_DISPLAY_NAME
      )
      self.platform_object.line_item_name_pattern = (
          bid2x_var.LINE_ITEM_NAME_PATTERN
      )
      self.platform_object.cb_tmp_file_prefix = bid2x_var.CB_TMP_FILE_PREFIX
      self.platform_object.cb_last_update_file_prefix = (
          bid2x_var.CB_LAST_UPDATE_FILE_PREFIX
      )
      self.platform_object.partner_id = bid2x_var.PARTNER_ID
      self.platform_object.advertiser_id = bid2x_var.ADVERTISER_ID
      self.platform_object.cb_algo_id = bid2x_var.CB_ALGO_ID
      self.platform_object.zones_to_process = bid2x_var.ZONES_TO_PROCESS
      self.platform_object.floodlight_id_list = bid2x_var.FLOODLIGHT_ID_LIST
      self.platform_object.attr_model_id = bid2x_var.ATTR_MODEL_ID
      self.platform_object.bidding_factor_high = bid2x_var.BIDDING_FACTOR_HIGH
      self.platform_object.bidding_factor_low = bid2x_var.BIDDING_FACTOR_LOW
