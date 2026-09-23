"""Tests for Bid2xApplication orchestration."""

from unittest.mock import MagicMock, patch

import bid2x_var
from bid2x_application import Bid2xApplication
import pytest


def _make_app(platform_type: str = 'DV') -> Bid2xApplication:
  with patch('bid2x_application.Bid2xSpreadsheet') as mock_sheet_cls, patch(
      'bid2x_application.Bid2xAuth'
  ) as mock_auth_cls:
    mock_sheet_cls.return_value = MagicMock(
        sheet_id='sheet-1', sheet_url='https://example.com/sheet'
    )
    mock_auth_cls.return_value = MagicMock()
    return Bid2xApplication(
        scopes='scope',
        api_name='displayvideo',
        api_version='v3',
        sheet_id='sheet-1',
        auth_file='secrets.json',
        platform_type=platform_type,
    )


def test_init_sets_defaults() -> None:
  app = _make_app()
  assert app.service is None
  assert app.debug is False
  assert app.trace is False
  assert app.platform_type == 'DV'
  assert app.zone_array == []
  assert app.platform_object is None


def test_getstate_omits_service() -> None:
  app = _make_app()
  app.service = MagicMock()
  state = app.__getstate__()
  assert 'service' not in state
  assert state['platform_type'] == 'DV'


def test_start_service_creates_dv_platform_object() -> None:
  app = _make_app('DV')
  with patch('bid2x_application.Bid2xDV') as mock_dv_cls:
    mock_dv_cls.return_value = MagicMock()
    app.start_service()
  mock_dv_cls.assert_called_once_with(app.sheet, app.debug)
  assert app.platform_object is mock_dv_cls.return_value


def test_authenticate_service_unknown_type_returns_false() -> None:
  app = _make_app()
  result = app.authenticate_service('secrets.json', None, 'UNKNOWN')
  assert result is False
  assert app.service is None


def test_assign_vars_to_objects_copies_dv_action_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  app = _make_app('DV')
  app.platform_object = MagicMock()
  monkeypatch.setattr(bid2x_var, 'PLATFORM_TYPE', 'DV')
  monkeypatch.setattr(bid2x_var, 'ACTION_TEST', True)
  monkeypatch.setattr(bid2x_var, 'ACTION_LIST_ALGOS', True)

  app.assign_vars_to_objects()

  assert app.platform_object.action_test is True
  assert app.platform_object.action_list_algos is True
  assert app.sheet.sheet_id == bid2x_var.SPREADSHEET_KEY
