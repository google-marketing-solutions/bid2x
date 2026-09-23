"""Tests for bid2x authentication helpers."""

from unittest import mock

from auth.bid2x_auth import Bid2xAuth


def test_auth_service_creds_loads_json_keyfile() -> None:
  auth = Bid2xAuth(['https://example.com/scope'], 'displayvideo', 'v3')
  mock_creds = mock.Mock()
  with mock.patch(
      'auth.bid2x_auth.ServiceAccountCredentials.from_json_keyfile_name',
      return_value=mock_creds,
  ) as load_creds:
    result = auth.auth_service_creds('client-secret.json')

  load_creds.assert_called_once_with(
      'client-secret.json',
      scopes=['https://example.com/scope'],
  )
  assert result is mock_creds


def test_auth_service_creds_applies_delegated_account() -> None:
  auth = Bid2xAuth(['scope-a'], 'displayvideo', 'v3')
  mock_creds = mock.Mock()
  delegated_creds = mock.Mock()
  mock_creds.create_delegated.return_value = delegated_creds
  with mock.patch(
      'auth.bid2x_auth.ServiceAccountCredentials.from_json_keyfile_name',
      return_value=mock_creds,
  ):
    result = auth.auth_service_creds(
        'client-secret.json',
        impersonation_email='user@example.com',
    )

  mock_creds.create_delegated.assert_called_once_with('user@example.com')
  assert result is delegated_creds


def test_auth_sheets_service_builds_sheets_client() -> None:
  auth = Bid2xAuth(['scope-a'], 'sheets', 'v4')
  mock_creds = mock.Mock()
  mock_service = mock.Mock()
  with mock.patch.object(
      auth, 'auth_service_creds', return_value=mock_creds
  ), mock.patch('auth.bid2x_auth.build', return_value=mock_service) as build:
    result = auth.auth_sheets_service('client-secret.json')

  build.assert_called_once_with('sheets', 'v4', credentials=mock_creds)
  assert result is mock_service
