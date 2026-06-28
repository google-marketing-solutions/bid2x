"""Tests for bid2x command-line argument parsing."""

import bid2x_var
from bid2x_args import apply_args_to_bid2x_var, build_argument_parser, process_command_line_args
import pytest


@pytest.fixture
def reset_bid2x_var_flags(monkeypatch: pytest.MonkeyPatch) -> None:
  monkeypatch.setattr(bid2x_var, 'DEBUG', False)
  monkeypatch.setattr(bid2x_var, 'TRACE', False)
  monkeypatch.setattr(bid2x_var, 'ACTION_TEST', False)
  monkeypatch.setattr(bid2x_var, 'FLOODLIGHT_ID_LIST', '1000001,1000002')
  monkeypatch.setattr(bid2x_var, 'INPUT_FILE', None)
  monkeypatch.setattr(bid2x_var, 'BIDDING_FACTOR_LOW', 0.5)


def test_build_argument_parser_exposes_debug_and_input_flags() -> None:
  parser = build_argument_parser()
  action_dests = {action.dest for action in parser._actions}
  assert 'debug' in action_dests
  assert 'input_file' in action_dests
  assert 'action_test' in action_dests


def test_apply_args_to_bid2x_var_sets_debug_and_input_file(
    reset_bid2x_var_flags: None,
) -> None:
  apply_args_to_bid2x_var({
      'action_list_algos': False,
      'action_list_scripts': False,
      'action_create': False,
      'action_update_spreadsheet': False,
      'action_remove': False,
      'action_update': False,
      'action_test': True,
      'debug': True,
      'verbose': False,
      'algo_name': bid2x_var.NEW_ALGO_NAME,
      'algo_display_name': bid2x_var.NEW_ALGO_DISPLAY_NAME,
      'json_file': 'secrets.json',
      'tmp': bid2x_var.CB_TMP_FILE_PREFIX,
      'last_upload': bid2x_var.CB_LAST_UPDATE_FILE_PREFIX,
      'input_file': 'config.json',
      'partner': bid2x_var.PARTNER_ID,
      'advertiser': bid2x_var.ADVERTISER_ID,
      'algorithm': bid2x_var.CB_ALGO_ID,
      'service_account': bid2x_var.SERVICE_ACCOUNT_EMAIL,
      'zones': 'zone-a',
      'floodlight': '1,2',
      'attribute': bid2x_var.ATTR_MODEL_ID,
      'bidding_high': bid2x_var.BIDDING_FACTOR_HIGH,
      'bidding_low': bid2x_var.BIDDING_FACTOR_LOW,
      'clear_onoff': False,
      'defer_pattern': False,
      'alt_algo': False,
      'li_pattern': bid2x_var.LINE_ITEM_NAME_PATTERN,
  })
  assert bid2x_var.DEBUG is True
  assert bid2x_var.ACTION_TEST is True
  assert bid2x_var.INPUT_FILE == 'config.json'
  assert bid2x_var.ZONES_TO_PROCESS == 'zone-a'


def test_process_command_line_args_parses_debug_flag(
    reset_bid2x_var_flags: None,
) -> None:
  process_command_line_args(['-d'])
  assert bid2x_var.DEBUG is True


def test_process_command_line_args_parses_bidding_low_as_float(
    reset_bid2x_var_flags: None,
) -> None:
  process_command_line_args(['-bl', '0.75'])
  assert bid2x_var.BIDDING_FACTOR_LOW == 0.75
