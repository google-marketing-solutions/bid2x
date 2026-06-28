"""BidToX - bid2x_config module.

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

  Typed configuration object for bid2x runtime settings. Parsed CLI and env
  values can be held here instead of mutating bid2x_var module globals
  directly. apply_to_bid2x_var() preserves backward compatibility during
  the Phase 3 migration.
"""

from dataclasses import dataclass
from typing import Any

import bid2x_var


def parse_floodlight_id_list(value: Any) -> list[str]:
  """Normalize floodlight input into a list of ID strings."""
  if isinstance(value, str):
    if ',' in value:
      return [part.strip() for part in value.split(',') if part.strip()]
    return value.split()
  if isinstance(value, list):
    return value
  return [str(value)]


@dataclass
class Bid2xConfig:
  """Runtime configuration parsed from CLI args or other sources."""

  action_list_algos: bool
  action_list_scripts: bool
  action_create_algorithm: bool
  action_update_spreadsheet: bool
  action_remove_algorithm: bool
  action_update_scripts: bool
  action_test: bool
  debug: bool
  trace: bool
  new_algo_name: str
  new_algo_display_name: str
  json_auth_file: str
  cb_tmp_file_prefix: str
  cb_last_update_file_prefix: str
  input_file: str | None
  partner_id: int
  advertiser_id: int
  cb_algo_id: int
  service_account_email: str
  zones_to_process: str
  floodlight_id_list: list[str]
  attr_model_id: int
  bidding_factor_high: float
  bidding_factor_low: float
  clear_onoff: bool
  defer_pattern: bool
  alternate_algorithm: bool
  line_item_name_pattern: str

  @classmethod
  def from_parsed_args(cls, args: dict[str, Any]) -> 'Bid2xConfig':
    """Build a config object from argparse namespace values."""
    return cls(
        action_list_algos=args['action_list_algos'],
        action_list_scripts=args['action_list_scripts'],
        action_create_algorithm=args['action_create'],
        action_update_spreadsheet=args['action_update_spreadsheet'],
        action_remove_algorithm=args['action_remove'],
        action_update_scripts=args['action_update'],
        action_test=args['action_test'],
        debug=args['debug'],
        trace=args['verbose'],
        new_algo_name=args['algo_name'],
        new_algo_display_name=args['algo_display_name'],
        json_auth_file=args['json_file'],
        cb_tmp_file_prefix=args['tmp'],
        cb_last_update_file_prefix=args['last_upload'],
        input_file=args['input_file'],
        partner_id=args['partner'],
        advertiser_id=args['advertiser'],
        cb_algo_id=args['algorithm'],
        service_account_email=args['service_account'],
        zones_to_process=args['zones'],
        floodlight_id_list=parse_floodlight_id_list(args['floodlight']),
        attr_model_id=args['attribute'],
        bidding_factor_high=args['bidding_high'],
        bidding_factor_low=args['bidding_low'],
        clear_onoff=args['clear_onoff'],
        defer_pattern=args['defer_pattern'],
        alternate_algorithm=args['alt_algo'],
        line_item_name_pattern=args['li_pattern'],
    )

  @classmethod
  def from_bid2x_var(cls) -> 'Bid2xConfig':
    """Snapshot current bid2x_var module globals as a config object."""
    floodlight = bid2x_var.FLOODLIGHT_ID_LIST
    return cls(
        action_list_algos=bid2x_var.ACTION_LIST_ALGOS,
        action_list_scripts=bid2x_var.ACTION_LIST_SCRIPTS,
        action_create_algorithm=bid2x_var.ACTION_CREATE_ALGORITHM,
        action_update_spreadsheet=bid2x_var.ACTION_UPDATE_SPREADSHEET,
        action_remove_algorithm=bid2x_var.ACTION_REMOVE_ALGORITHM,
        action_update_scripts=bid2x_var.ACTION_UPDATE_SCRIPTS,
        action_test=bid2x_var.ACTION_TEST,
        debug=bid2x_var.DEBUG,
        trace=bid2x_var.TRACE,
        new_algo_name=bid2x_var.NEW_ALGO_NAME,
        new_algo_display_name=bid2x_var.NEW_ALGO_DISPLAY_NAME,
        json_auth_file=bid2x_var.JSON_AUTH_FILE,
        cb_tmp_file_prefix=bid2x_var.CB_TMP_FILE_PREFIX,
        cb_last_update_file_prefix=bid2x_var.CB_LAST_UPDATE_FILE_PREFIX,
        input_file=bid2x_var.INPUT_FILE,
        partner_id=bid2x_var.PARTNER_ID,
        advertiser_id=bid2x_var.ADVERTISER_ID,
        cb_algo_id=bid2x_var.CB_ALGO_ID,
        service_account_email=bid2x_var.SERVICE_ACCOUNT_EMAIL,
        zones_to_process=bid2x_var.ZONES_TO_PROCESS,
        floodlight_id_list=parse_floodlight_id_list(floodlight),
        attr_model_id=bid2x_var.ATTR_MODEL_ID,
        bidding_factor_high=bid2x_var.BIDDING_FACTOR_HIGH,
        bidding_factor_low=bid2x_var.BIDDING_FACTOR_LOW,
        clear_onoff=bid2x_var.CLEAR_ONOFF,
        defer_pattern=bid2x_var.DEFER_PATTERN,
        alternate_algorithm=bid2x_var.ALTERNATE_ALGORITHM,
        line_item_name_pattern=bid2x_var.LINE_ITEM_NAME_PATTERN,
    )

  def apply_to_bid2x_var(self) -> None:
    """Copy this config into bid2x_var module globals."""
    bid2x_var.ACTION_LIST_ALGOS = self.action_list_algos
    bid2x_var.ACTION_LIST_SCRIPTS = self.action_list_scripts
    bid2x_var.ACTION_CREATE_ALGORITHM = self.action_create_algorithm
    bid2x_var.ACTION_UPDATE_SPREADSHEET = self.action_update_spreadsheet
    bid2x_var.ACTION_REMOVE_ALGORITHM = self.action_remove_algorithm
    bid2x_var.ACTION_UPDATE_SCRIPTS = self.action_update_scripts
    bid2x_var.ACTION_TEST = self.action_test
    bid2x_var.DEBUG = self.debug
    bid2x_var.TRACE = self.trace
    bid2x_var.NEW_ALGO_NAME = self.new_algo_name
    bid2x_var.NEW_ALGO_DISPLAY_NAME = self.new_algo_display_name
    bid2x_var.JSON_AUTH_FILE = self.json_auth_file
    bid2x_var.CB_TMP_FILE_PREFIX = self.cb_tmp_file_prefix
    bid2x_var.CB_LAST_UPDATE_FILE_PREFIX = self.cb_last_update_file_prefix
    bid2x_var.INPUT_FILE = self.input_file
    bid2x_var.PARTNER_ID = self.partner_id
    bid2x_var.ADVERTISER_ID = self.advertiser_id
    bid2x_var.CB_ALGO_ID = self.cb_algo_id
    bid2x_var.SERVICE_ACCOUNT_EMAIL = self.service_account_email
    bid2x_var.ZONES_TO_PROCESS = self.zones_to_process
    bid2x_var.FLOODLIGHT_ID_LIST = self.floodlight_id_list
    bid2x_var.ATTR_MODEL_ID = self.attr_model_id
    bid2x_var.BIDDING_FACTOR_HIGH = self.bidding_factor_high
    bid2x_var.BIDDING_FACTOR_LOW = self.bidding_factor_low
    bid2x_var.CLEAR_ONOFF = self.clear_onoff
    bid2x_var.DEFER_PATTERN = self.defer_pattern
    bid2x_var.ALTERNATE_ALGORITHM = self.alternate_algorithm
    bid2x_var.LINE_ITEM_NAME_PATTERN = self.line_item_name_pattern
