"""Tests for main.py entry-point behavior."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Cloud Function decorator stub must exist before main is imported.
_mock_functions_framework = MagicMock()
_mock_functions_framework.cloud_event = lambda fn: fn
sys.modules.setdefault('functions_framework', _mock_functions_framework)

import main  # noqa: E402


def test_module_import_does_not_bootstrap_app() -> None:
  assert main.app is None


def test_initialize_app_parses_args_and_sets_global_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
  mock_app = MagicMock()
  monkeypatch.setattr(main, 'app', None)

  with patch.object(main, 'process_command_line_args') as mock_parse, patch.object(
      main, 'create_objects_from_json_file', return_value=mock_app
  ) as mock_create:
    result = main.initialize_app()

  mock_parse.assert_called_once_with()
  mock_create.assert_called_once_with(main.bid2x_var.INPUT_FILE)
  assert result is mock_app
  assert main.app is mock_app


def test_main_returns_error_when_app_not_initialized() -> None:
  original_app = main.app
  main.app = None
  try:
    assert main.main(['main.py']) == -1
  finally:
    main.app = original_app
