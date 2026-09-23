"""Tests for environment variable parsing."""

import bid2x_var
from bid2x_env import parse_bool, process_environment_vars
import pytest


@pytest.mark.parametrize(
    'value',
    ['y', 'yes', 't', 'true', 'on', '1', 'Y', 'TRUE'],
)
def test_parse_bool_accepts_truthy_strings(value: str) -> None:
  assert parse_bool(value) is True


@pytest.mark.parametrize(
    'value',
    ['n', 'no', 'f', 'false', 'off', '0', 'FALSE'],
)
def test_parse_bool_accepts_falsy_strings(value: str) -> None:
  assert parse_bool(value) is False


def test_parse_bool_accepts_bool_values() -> None:
  assert parse_bool(True) is True
  assert parse_bool(False) is False


def test_parse_bool_rejects_invalid_strings() -> None:
  with pytest.raises(ValueError, match='invalid truth value'):
    parse_bool('maybe')


def test_process_environment_vars_sets_debug_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv('DEBUG', 'true')
  bid2x_var.DEBUG = False
  process_environment_vars()
  assert bid2x_var.DEBUG is True


def test_process_environment_vars_keeps_bool_default_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.delenv('DEBUG', raising=False)
  monkeypatch.delenv('ACTION_TEST', raising=False)
  bid2x_var.DEBUG = False
  bid2x_var.ACTION_TEST = False
  process_environment_vars()
  assert bid2x_var.DEBUG is False
  assert bid2x_var.ACTION_TEST is False


def test_process_environment_vars_sets_string_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv('ZONES_TO_PROCESS', 'zone-a,zone-b')
  process_environment_vars()
  assert bid2x_var.ZONES_TO_PROCESS == 'zone-a,zone-b'


def test_process_environment_vars_sets_numeric_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  monkeypatch.setenv('PARTNER_ID', '424242')
  process_environment_vars()
  assert bid2x_var.PARTNER_ID == 424242
