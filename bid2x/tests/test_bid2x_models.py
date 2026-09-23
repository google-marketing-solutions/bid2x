"""Tests for DV and GTM zone model classes."""

from bid2x_gtm_model import Bid2xGTMModel
from bid2x_model import Bid2xModel


def _make_dv_model() -> Bid2xModel:
  return Bid2xModel(
      name='zone-a',
      campaign_id=100,
      advertiser_id=200,
      algorithm_id=300,
      debug=False,
      update_row=2,
      update_col=3,
      test_row=4,
      test_col=5,
  )


def _make_gtm_model() -> Bid2xGTMModel:
  return Bid2xGTMModel(
      name='gtm-zone-a',
      account_id=10,
      container_id=20,
      workspace_id=30,
      variable_id=40,
      update_row=2,
      update_col=3,
      test_row=4,
      test_col=5,
  )


def test_bid2x_model_str_includes_core_fields() -> None:
  model = _make_dv_model()
  rendered = str(model)
  assert 'zone-a' in rendered
  assert 'campaign_id: 100' in rendered
  assert 'algorithm_id: 300' in rendered
  assert 'test_col: 5' in rendered


def test_bid2x_model_initializes_cb_algorithm_empty() -> None:
  model = _make_dv_model()
  assert model.cb_algorithm == ''


def test_bid2x_model_set_spreadsheet_row_col() -> None:
  model = _make_dv_model()
  model.set_spreadsheet_row_col(10, 11, 12, 13)
  assert model.update_row == 10
  assert model.update_col == 11
  assert model.test_row == 12
  assert model.test_col == 13


def test_bid2x_gtm_model_str_matches_dv_formatting() -> None:
  model = _make_gtm_model()
  rendered = str(model)
  assert 'gtm-zone-a' in rendered
  assert 'variable_id: 40' in rendered
  assert 'update_row: 2' in rendered
  assert 'test_col: 5' in rendered


def test_bid2x_gtm_model_defaults_debug_and_trace_to_false() -> None:
  model = _make_gtm_model()
  assert model.debug is False
  assert model.trace is False


def test_bid2x_gtm_model_set_cb_algorithm() -> None:
  model = _make_gtm_model()
  model.set_cb_algorithm('lookup-table')
  assert model.cb_algorithm == 'lookup-table'
