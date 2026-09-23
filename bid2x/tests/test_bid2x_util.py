"""Tests for bid2x utility helpers."""

from typing import Any
from unittest import mock

import bid2x_util
from bid2x_util import (
    copy_iff_exists,
    google_dv_call,
    is_number,
    is_recoverable_http_error,
    read_config,
    save_config,
)
from googleapiclient import errors
import http
import pytest

HTTPStatus = http.HTTPStatus
HttpError = errors.HttpError


@pytest.mark.parametrize(
    'value',
    [1, 1.5, '42', '3.14'],
)
def test_is_number_accepts_numeric_values(value: Any) -> None:
  assert is_number(value) is True


@pytest.mark.parametrize(
    'value',
    ['', 'abc', None, {}, []],
)
def test_is_number_rejects_non_numeric_values(value: Any) -> None:
  assert is_number(value) is False


@pytest.mark.parametrize(
    'status',
    [
        HTTPStatus.FORBIDDEN,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ],
)
def test_is_recoverable_http_error_accepts_retryable_statuses(
    status: HTTPStatus,
) -> None:
  assert is_recoverable_http_error(status) is True


def test_is_recoverable_http_error_rejects_other_statuses() -> None:
  assert is_recoverable_http_error(HTTPStatus.BAD_REQUEST) is False


def test_copy_iff_exists_copies_present_key() -> None:
  src = {'name': 'zone-a', 'missing': 1}
  dst: dict[str, Any] = {}
  copy_iff_exists(src, 'name', dst)
  assert dst == {'name': 'zone-a'}


def test_copy_iff_exists_skips_missing_key() -> None:
  src = {'name': 'zone-a'}
  dst: dict[str, Any] = {'existing': True}
  copy_iff_exists(src, 'absent', dst)
  assert dst == {'existing': True}


def test_save_and_read_config_roundtrip(tmp_path: Any) -> None:
  config_path = tmp_path / 'config.json'
  payload = {'platform_type': 'DV', 'debug': False}
  save_config(payload, str(config_path))
  loaded = read_config(str(config_path))
  assert loaded == payload


def test_read_config_raises_for_missing_local_file(tmp_path: Any) -> None:
  missing_path = tmp_path / 'missing.json'
  with pytest.raises(FileNotFoundError):
    read_config(str(missing_path))


def test_google_dv_call_returns_execute_response() -> None:
  request = mock.Mock()
  request.execute.return_value = {'items': []}
  assert google_dv_call(request, 'list items') == {'items': []}
  request.execute.assert_called_once_with()


def test_google_dv_call_retries_recoverable_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  request = mock.Mock()
  response = mock.Mock(status=HTTPStatus.FORBIDDEN)
  request.execute.side_effect = [
      HttpError(response, b'rate limited'),
      {'items': ['ok']},
  ]
  monkeypatch.setattr(bid2x_util.time, 'sleep', lambda _: None)
  assert google_dv_call(request, 'list items') == {'items': ['ok']}
  assert request.execute.call_count == 2


def test_google_dv_call_reraises_non_recoverable_http_error() -> None:
  request = mock.Mock()
  response = mock.Mock(status=HTTPStatus.BAD_REQUEST)
  request.execute.side_effect = HttpError(response, b'bad request')
  with pytest.raises(HttpError):
    google_dv_call(request, 'list items')
