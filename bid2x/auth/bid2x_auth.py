"""BidToX - Authentication for bid2x objects.

  Copyright 2025 Google LLC

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  Description:
  ------------

  This module contains the authentication functions for the bid2x application.
"""

from typing import Any

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

build = discovery.build


class Bid2xAuth:
  """Authenticate bid2x service accounts for Google APIs."""

  _scopes: list[str] | str
  _service: Any
  _api_name: str
  _api_version: str

  def __init__(
      self, scopes: list[str] | str, api_name: str, api_version: str
  ) -> None:
    self._scopes = scopes
    self._api_name = api_name
    self._api_version = api_version
    self._service = None

  def auth_service_creds(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str | None = None,
  ) -> ServiceAccountCredentials:
    """Authorizes an httplib2.Http instance using service account credentials.

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address.

    Returns:
      Returns service account credentials.
    """

    # Load the service account credentials from the specified JSON keyfile.
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        path_to_service_account_json_file, scopes=self._scopes
    )
    # Configure impersonation (if applicable).
    if impersonation_email:
      credentials = credentials.create_delegated(impersonation_email)

    return credentials

  def auth_gtm_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str | None = None,
  ) -> Any:
    """Create an authenticated Google Tag Manager API service.

    Args:
      path_to_service_account_json_file: An authentication file in json format.
      impersonation_email: Optional delegated service account email.

    Returns:
      The authenticated GTM API service resource, or None if credentials fail.
    """

    # Load the service account credentials from the specified JSON keyfile.
    service_credentials = self.auth_service_creds(
        path_to_service_account_json_file, impersonation_email
    )

    # Build the GTM service object.
    if service_credentials:
      self._service = discovery.build(
          self._api_name, self._api_version, credentials=service_credentials
      )

      return self._service

  def auth_dv(
      self, auth_file: str, auth_email_account: str | None = None
  ) -> Any:
    """Create an authenticated DV360 API service.

    Args:
      auth_file: An authentication file in json format.
      auth_email_account: Optional delegated service account email.

    Returns:
      The authenticated DV360 API service resource.

    Raises:
      ValueError: If authentication fails.
    """
    dv_http_service = self.auth_dv_service(auth_file, auth_email_account)

    # Build a service object for interacting with the API.
    if dv_http_service:
      self._service = discovery.build(
          self._api_name, self._api_version, http=dv_http_service
      )
    else:
      raise ValueError('Error authenticating using provided JSON information')

    return self._service

  def auth_dv_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str | None = None,
  ) -> Any:
    """Create an authenticated DV360 API service using service account creds.

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: Optional delegated service account email.

    Returns:
      The authenticated DV360 API service resource, or None if credentials fail.
    """

    # Load the service account credentials from the specified JSON keyfile.
    service_credentials = self.auth_service_creds(
        path_to_service_account_json_file, impersonation_email
    )

    discovery_url = (
        'https://displayvideo.googleapis.com/$discovery'
        f'/rest?version={self._api_version}'
    )

    if service_credentials:
      self._service = discovery.build(
          self._api_name,
          self._api_version,
          credentials=service_credentials,
          discoveryServiceUrl=discovery_url,
      )

    return self._service

  def auth_sheets(
      self, auth_file: str, auth_email_account: str | None = None
  ) -> Any:
    """Create an authenticated Google Sheets API service.

    Args:
      auth_file: file downloaded from GCP
      auth_email_account: Optional delegated service account email.

    Returns:
      The authenticated Sheets API service resource.

    Raises:
      ValueError: If authentication fails.
    """

    # Set up service object to talk to Google Sheets.
    sheets_service = self.auth_sheets_service(auth_file, auth_email_account)

    # Build a service object for interacting with the API.
    if not sheets_service:
      raise ValueError(
          'Error authenticating sheets using provided JSON information'
      )

    return sheets_service

  def auth_sheets_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str | None = None,
  ) -> Any:
    """Create an authenticated Google Sheets API service.

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: Optional delegated service account email.

    Returns:
      The authenticated Sheets API service resource.
    """

    # Authorizes an httplib2.Http instance using service account credentials.
    creds = self.auth_service_creds(path_to_service_account_json_file,
                                    impersonation_email)
    service = build('sheets', 'v4', credentials=creds)

    return service
