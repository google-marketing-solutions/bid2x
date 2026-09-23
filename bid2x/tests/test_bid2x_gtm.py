"""Tests for GTM JavaScript generation in bid2x_gtm."""

import re
from unittest.mock import MagicMock

import bid2x_var
from bid2x_gtm import Bid2xGTM, GTMConfigurationError, GTMFloodlight
import pandas as pd
import pytest


def _make_gtm() -> Bid2xGTM:
  return Bid2xGTM(MagicMock(), debug=False)


def test_generate_multipliers_js_builds_nested_object() -> None:
  gtm = _make_gtm()
  df = pd.DataFrame({
      'region': ['US', 'UK'],
      'Index': [1.5, 2.0],
  })

  result = gtm.generate_multipliers_js(df, 'Index', 'region')

  assert result.startswith('  var multipliers = ')
  assert '"US": 1.5' in result
  assert '"UK": 2.0' in result


def test_generate_get_multiplier_js_function_uses_generic_params() -> None:
  gtm = _make_gtm()

  result = gtm.generate_get_multiplier_js_function(['region', 'model'])

  assert 'function getMultiplier(var1, var2)' in result
  assert '|| 1.0' in result


def test_generate_js_function_call_empty_dimensions_returns_string() -> None:
  gtm = _make_gtm()

  result = gtm.generate_js_function_call([])

  assert isinstance(result, str)
  assert 'getMultiplier' in result


def test_replace_match_substitutes_row_value() -> None:
  gtm = _make_gtm()
  match = re.search(r'#([^#]+)#', '#region#')
  assert match is not None

  assert gtm.replace_match(match, pd.Series({'region': 'US'})) == 'US'


def test_write_javascript_function_generates_expected_structure() -> None:
  gtm = _make_gtm()
  gtm.gtm_floodlight_list = [
      GTMFloodlight(
          floodlight_name='purchase',
          per_row_condition="#region# == 'US'",
          total_var='revenue',
      )
  ]
  df = pd.DataFrame({
      'region': ['US'],
      bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value: ['1.2'],
  })

  result = gtm.write_javascript_function(df)

  assert result.startswith('function() {')
  assert 'return conversion_value;' in result
  assert 'purchase' in result
  assert '1.2' in result


def test_write_javascript_function_lookup_mode_includes_multipliers() -> None:
  gtm = _make_gtm()
  gtm.gtm_floodlight_list = [
      GTMFloodlight(
          floodlight_name='purchase',
          per_row_condition='lookup#region',
          total_var='revenue',
      )
  ]
  df = pd.DataFrame({
      'region': ['US', 'UK'],
      'Index': [1.1, 0.9],
  })

  result = gtm.write_javascript_function(df)

  assert 'var multipliers =' in result
  assert 'function getMultiplier' in result
  assert 'conversion_value *= getMultiplier' in result


def test_write_javascript_function_raises_without_per_row_condition() -> None:
  gtm = _make_gtm()

  class FloodlightWithoutCondition:
    floodlight_name = 'purchase'
    total_var = 'revenue'

  gtm.gtm_floodlight_list = [FloodlightWithoutCondition()]
  df = pd.DataFrame({
      'region': ['US'],
      bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value: ['1.2'],
  })

  with pytest.raises(GTMConfigurationError):
    gtm.write_javascript_function(df)
