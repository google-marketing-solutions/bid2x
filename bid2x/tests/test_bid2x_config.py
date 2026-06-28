"""Tests for bid2x configuration object."""

import bid2x_var
from bid2x_config import Bid2xConfig, parse_floodlight_id_list


def _sample_parsed_args(**overrides: object) -> dict[str, object]:
  args: dict[str, object] = {
      'action_list_algos': False,
      'action_list_scripts': False,
      'action_create': False,
      'action_update_spreadsheet': False,
      'action_remove': False,
      'action_update': False,
      'action_test': False,
      'debug': False,
      'verbose': False,
      'algo_name': bid2x_var.NEW_ALGO_NAME,
      'algo_display_name': bid2x_var.NEW_ALGO_DISPLAY_NAME,
      'json_file': bid2x_var.JSON_AUTH_FILE,
      'tmp': bid2x_var.CB_TMP_FILE_PREFIX,
      'last_upload': bid2x_var.CB_LAST_UPDATE_FILE_PREFIX,
      'input_file': bid2x_var.INPUT_FILE,
      'partner': bid2x_var.PARTNER_ID,
      'advertiser': bid2x_var.ADVERTISER_ID,
      'algorithm': bid2x_var.CB_ALGO_ID,
      'service_account': bid2x_var.SERVICE_ACCOUNT_EMAIL,
      'zones': bid2x_var.ZONES_TO_PROCESS,
      'floodlight': bid2x_var.FLOODLIGHT_ID_LIST,
      'attribute': bid2x_var.ATTR_MODEL_ID,
      'bidding_high': bid2x_var.BIDDING_FACTOR_HIGH,
      'bidding_low': bid2x_var.BIDDING_FACTOR_LOW,
      'clear_onoff': False,
      'defer_pattern': False,
      'alt_algo': False,
      'li_pattern': bid2x_var.LINE_ITEM_NAME_PATTERN,
  }
  args.update(overrides)
  return args


def test_parse_floodlight_id_list_splits_commas() -> None:
  assert parse_floodlight_id_list('1000001,1000002') == [
      '1000001',
      '1000002',
  ]


def test_parse_floodlight_id_list_splits_whitespace() -> None:
  assert parse_floodlight_id_list('1 2 3') == ['1', '2', '3']


def test_from_bid2x_var_roundtrip() -> None:
  config = Bid2xConfig.from_bid2x_var()
  config.apply_to_bid2x_var()
  assert bid2x_var.DEBUG == config.debug
  assert bid2x_var.JSON_AUTH_FILE == config.json_auth_file
  assert bid2x_var.FLOODLIGHT_ID_LIST == config.floodlight_id_list


def test_from_parsed_args_applies_floodlight_commas() -> None:
  config = Bid2xConfig.from_parsed_args(
      _sample_parsed_args(floodlight='9,10')
  )
  assert config.floodlight_id_list == ['9', '10']
  config.apply_to_bid2x_var()
  assert bid2x_var.FLOODLIGHT_ID_LIST == ['9', '10']
