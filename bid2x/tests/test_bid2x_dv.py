"""Tests for DV360 custom bidding script generation in bid2x_dv."""

from unittest.mock import MagicMock

from bid2x_dv import Bid2xDV


def _make_dv(**overrides: object) -> Bid2xDV:
  dv = Bid2xDV(MagicMock(), debug=False)
  dv.floodlight_id_list = ['1000001', '1000002']
  dv.attr_model_id = 0
  dv.bidding_factor_low = 0.5
  dv.bidding_factor_high = 1000.0
  for key, value in overrides.items():
    setattr(dv, key, value)
  return dv


def test_init_defaults() -> None:
  dv = Bid2xDV(MagicMock(), debug=False)
  assert dv.action_test is False
  assert dv.clear_onoff is False
  assert dv.floodlight_id_list == []


def test_build_cb_script_returns_zero_when_no_rows_selected() -> None:
  dv = _make_dv()
  rows = [
      {
          'Generate Custom Bidding': 'No',
          'Bidding Factor': 1.5,
          'Line Item ID': 12345,
      }
  ]

  assert dv._build_cb_script_from_rows(rows) == 'return 0;'


def test_build_cb_script_max_aggregate_includes_line_items() -> None:
  dv = _make_dv()
  rows = [
      {
          'Generate Custom Bidding': 'Yes',
          'Bidding Factor': 1.5,
          'Line Item ID': 12345,
      }
  ]

  script = dv._build_cb_script_from_rows(rows)

  assert script.startswith('return max_aggregate([')
  assert 'line_item_id == 12345' in script
  assert '1000001' in script
  assert '1000002' in script
  assert script.endswith('])')


def test_build_cb_script_clamps_bidding_factor() -> None:
  dv = _make_dv(bidding_factor_high=2.0)
  rows = [
      {
          'Generate Custom Bidding': 'Yes',
          'Bidding Factor': 99.0,
          'Line Item ID': 999,
      }
  ]

  script = dv._build_cb_script_from_rows(rows)

  assert 'line_item_id == 999' in script
  assert '2.0),' in script or '2.0)' in script


def test_build_cb_script_alternate_algorithm_uses_if_blocks() -> None:
  dv = _make_dv(alternate_algorithm=True, floodlight_id_list=['1000001'])
  rows = [
      {
          'Generate Custom Bidding': 'Yes',
          'Bidding Factor': 1.25,
          'Line Item ID': 555,
      }
  ]

  script = dv._build_cb_script_from_rows(rows)

  assert 'if line_item_id == 555:' in script
  assert 'return total_conversion_count(1000001,0) * 1.25' in script
  assert 'else:\n  return 0' in script


def test_write_and_read_last_upload_file(tmp_path) -> None:
  dv = _make_dv()
  script_path = tmp_path / 'last_upload_zone.txt'

  assert dv.write_last_upload_file(str(script_path), 'custom bidding body') is True
  assert dv.read_last_upload_file(str(script_path)) == 'custom bidding body'
