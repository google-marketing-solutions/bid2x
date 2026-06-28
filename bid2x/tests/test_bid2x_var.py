"""Smoke tests for bid2x default configuration values."""

import bid2x_var


def test_platform_type_defaults_to_dv() -> None:
  assert bid2x_var.PLATFORM_TYPE == 'DV'


def test_action_flags_default_to_false() -> None:
  assert bid2x_var.ACTION_LIST_ALGOS is False
  assert bid2x_var.ACTION_LIST_SCRIPTS is False
  assert bid2x_var.ACTION_CREATE_ALGORITHM is False
  assert bid2x_var.ACTION_UPDATE_SPREADSHEET is False
  assert bid2x_var.ACTION_REMOVE_ALGORITHM is False
  assert bid2x_var.ACTION_UPDATE_SCRIPTS is False
  assert bid2x_var.ACTION_TEST is False


def test_platform_type_enum_values() -> None:
  assert bid2x_var.PlatformType.DV.value == 'DV'
  assert bid2x_var.PlatformType.GTM.value == 'GTM'
  assert bid2x_var.PlatformType.SHEETS.value == 'SHEETS'


def test_bidding_factor_bounds() -> None:
  assert bid2x_var.BIDDING_FACTOR_LOW < bid2x_var.BIDDING_FACTOR_HIGH
