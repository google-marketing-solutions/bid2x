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


def test_debug_and_trace_default_to_false() -> None:
  assert bid2x_var.DEBUG is False
  assert bid2x_var.TRACE is False


def test_auth_defaults_are_singular() -> None:
  assert bid2x_var.JSON_AUTH_FILE == 'client-secret.json'
  assert (
      bid2x_var.SERVICE_ACCOUNT_EMAIL
      == 'bid-to-x@client-gcp.iam.gserviceaccount.com'
  )
