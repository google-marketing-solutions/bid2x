"""BidToX - Authentication for bid2x objects.

  Copyright 2025 Google Inc.

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

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials


<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
build = discovery.build
=======
class bid2x_auth():
    """
      Authentication for bid2x objects.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
=======
      Attributes:
          _scopes (str): The name of the dog.
          _service (Resource):
          _api_name (str): The breed of the dog.
          _api_version (str): The age of the dog in years.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
class Bid2xAuth:
  """Authentication for bid2x objects.

  Attributes:
      _scopes (str): The name of the dog.
      _service (Resource):
      _api_name (str): The breed of the dog.
      _api_version (str): The age of the dog in years.

  Methods:
      auth_service_creds(self,
                          path_to_service_account_json_file):
          Authenticates the service account.
      auth_gtm_service(self,
                        path_to_service_account_json_file,
                        impersonation_email):
          Creates the GTM resource after authenticating credentials.
      auth_dv(self, auth_file, auth_email_account):
          Creates the DV360 resource after authenticating credentials.
      auth_dv_service(self,
                      path_to_service_account_json_file,
                      impersonation_email):
          Creates the DV360 resource after authenticating credentials.
      auth_sheets(self, auth_file: str, auth_email_account: str=None):
          Creates Google sheets credentials based on a service account
          and email.
      auth_sheets_service(self,
                          path_to_service_account_json_file,
                          impersonation_email)
          Creates Google sheets credentials based on a service account
          and email.
  """

  _scopes: str
=======
      Methods:
          auth_service_creds(self,
                             path_to_service_account_json_file):
              Authenticates the service account.
          auth_gtm_service(self,
                           path_to_service_account_json_file,
                           impersonation_email):
              Creates the GTM resource after authenticating credentials.
          auth_dv(self, auth_file, auth_email_account):
              Creates the DV360 resource after authenticating credentials.
          auth_dv_service(self,
                          path_to_service_account_json_file,
                          impersonation_email):
              Creates the DV360 resource after authenticating credentials.
          auth_sheets(self, auth_file: str, auth_email_account: str=None):
              Creates Google sheets credentials based on a service account
              and email.
          auth_sheets_service(self,
                              path_to_service_account_json_file,
                              impersonation_email)
              Creates Google sheets credentials based on a service account
              and email.
    """
    _scopes: str
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  _service = None
  _api_name: str
  _api_version: str
=======
    service = None
    _api_name: str
    _api_version: str
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def __init__(self, scopes: str, api_name: str, api_version: str):
    self._scopes = scopes
    self._api_name = api_name
    self._api_version = api_version
    self._service = None
=======
    def __init__(self,
                 scopes: str,
                 api_name: str,
                 api_version: str):
        self._scopes = scopes
        self._api_name = api_name
        self._api_version = api_version
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def auth_service_creds(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str = None,
  ) -> ServiceAccountCredentials:
    """Authorizes an httplib2.Http instance using service account credentials.
=======
    def auth_service_creds(self,
                           path_to_service_account_json_file: str,
                           impersonation_email: str = None) -> ServiceAccountCredentials:

        """Authorizes an httplib2.Http instance
        using service account credentials."""

        # Load the service account credentials from the specified JSON keyfile.
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            path_to_service_account_json_file,
            scopes=self._scopes)
        # Configure impersonation (if applicable).
        if impersonation_email:
            credentials = credentials.create_delegated(impersonation_email)

        return credentials

    def auth_gtm_service(self,
                         path_to_service_account_json_file: str,
                         impersonation_email: str=None) -> discovery.Resource:
        """Top level function for auth'ing to Google Tag Manager.
        Args:
          path_to_service_account_json_file: An authentication file in json format.
          impersonation_email: The email account (typically a service account)
            under which the auth file is to be used.
        Returns:
          Returns True if able to create a good .service object
          within this class, otherwise it returns False.
        """
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address.

    Returns:
      Returns service account credentials.
    """
=======
        # Load the service account credentials from the specified JSON keyfile.
        service_credentials = self.auth_service_creds(
          path_to_service_account_json_file,
          impersonation_email)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Load the service account credentials from the specified JSON keyfile.
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        path_to_service_account_json_file, scopes=self._scopes
    )
    # Configure impersonation (if applicable).
    if impersonation_email:
      credentials = credentials.create_delegated(impersonation_email)
=======
        # Build the GTM service object.
        if service_credentials:
            self.service = discovery.build( self._api_name,
                                            self._api_version,
                                            credentials=service_credentials)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

        return self.service

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def auth_gtm_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str = None,
  ) -> discovery.Resource:
    """Top level function for auth'ing to Google Tag Manager.

    Args:
      path_to_service_account_json_file: An authentication file in json format.
      impersonation_email: The email account (typically a service account) under
        which the auth file is to be used.

    Returns:
      Returns True if able to create a good .service object
      within this class, otherwise it returns False.
    """
=======
    def auth_dv(self, auth_file: str, auth_email_account: str=None) -> discovery.Resource:
        """Top level function for auth'ing to DV360.
        Args:
          auth_file: An authentication file in json format.
          auth_email_account: The email account (typically a service account)
            under which the auth file is to be used.
        Returns:
          Returns True if able to create a good .service object
          within this class, otherwise it returns False.
        Raises:
          ValueError: If authentication fails.
        """
        dv_http_service = self.auth_dv_service(auth_file, auth_email_account)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Load the service account credentials from the specified JSON keyfile.
    service_credentials = self.auth_service_creds(
        path_to_service_account_json_file, impersonation_email
    )
=======
        # Build a service object for interacting with the API.
        if dv_http_service:
            self.service = discovery.build(
                self._api_name,
                self._api_version,
                http=dv_http_service)
        else:
            raise ValueError("Error authenticating using provided JSON information")
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # discovery_url = (f'https://tagmanager.googleapis.com/$discovery'
    #                  f'/rest?version={self._api_version}')

    print(
        f'bid2x_auth.auth_gtm_service - api_name:{self._api_name},',
        f' api_version:{self._api_version}',
    )
=======
        return self.service
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Build the GTM service object.
    if service_credentials:
      self._service = discovery.build(
          self._api_name, self._api_version, credentials=service_credentials
      )
=======
    def auth_dv_service(self,
                        path_to_service_account_json_file: str,
                        impersonation_email: str=None) -> discovery.Resource:
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
      return self._service
=======
        """Creates DV credentials based on a service account and email.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def auth_dv(
      self, auth_file: str, auth_email_account: str = None
  ) -> discovery.Resource:
    """Top level function for auth'ing to DV360.

    Args:
      auth_file: An authentication file in json format.
      auth_email_account: The email account (typically a service account) under
        which the auth file is to be used.

    Returns:
      Returns True if able to create a good .service object
      within this class, otherwise it returns False.
    Raises:
      ValueError: If authentication fails.
    """
    dv_http_service = self.auth_dv_service(auth_file, auth_email_account)
=======
        Args:
          path_to_service_account_json_file: file downloaded from GCP
          impersonation_email: service account email address.

        Returns:
          Returns http object.
        """
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Build a service object for interacting with the API.
    if dv_http_service:
      self._service = discovery.build(
          self._api_name, self._api_version, http=dv_http_service
      )
    else:
      raise ValueError('Error authenticating using provided JSON information')
=======
        """Performs OAuth2 for a DV360 service using
        service account credentials."""
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return self._service
=======
        # Load the service account credentials from the specified JSON keyfile.
        service_credentials = self.auth_service_creds(
            path_to_service_account_json_file,
            impersonation_email)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def auth_dv_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str = None,
  ) -> discovery.Resource:
    """Creates DV credentials based on a service account and email.

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address.
=======
        discovery_url = (f'https://displayvideo.googleapis.com/$discovery'
                         f'/rest?version={self._api_version}')

        if service_credentials:
            self.service = discovery.build(self._api_name,
                                           self._api_version,
                                           credentials=service_credentials,
                                           discoveryServiceUrl=discovery_url)
        return self.service
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
      Returns http object.
    """
=======
    def auth_sheets(self, auth_file: str, auth_email_account: str=None) -> discovery.Resource:
        """Creates Google sheets credentials based on a service account and email.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Load the service account credentials from the specified JSON keyfile.
    service_credentials = self.auth_service_creds(
        path_to_service_account_json_file, impersonation_email
    )
=======
        Args:
          auth_file: file downloaded from GCP
          auth_email_account: service account email address.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    discovery_url = (
        'https://displayvideo.googleapis.com/$discovery'
        f'/rest?version={self._api_version}'
    )
=======
        Returns:
          Returns http object.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if service_credentials:
      self._service = discovery.build(
          self._api_name,
          self._api_version,
          credentials=service_credentials,
          discoveryServiceUrl=discovery_url,
      )

    return self._service
=======
        Raises:
          ValueError: If authentication fails.
        """
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def auth_sheets(
      self, auth_file: str, auth_email_account: str = None
  ) -> discovery.Resource:
    """Creates Google sheets credentials based on a service account and email.
=======
        # Set up service object to talk to Google Sheets.
        sheets_service = self.auth_sheets_service(auth_file, auth_email_account)

        # Build a service object for interacting with the API.
        if not sheets_service:
            raise ValueError("Error authenticating sheets using provided JSON information")
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

        return sheets_service

    def auth_sheets_service(self,
                            path_to_service_account_json_file: str,
                            impersonation_email: str=None) -> discovery.Resource:
        """Creates Google sheets credentials based on a service account and email.

        Args:
          path_to_service_account_json_file: file downloaded from GCP
          impersonation_email: service account email address.

        Returns:
          Returns http object.
        """

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Build a service object for interacting with the API.
    if not sheets_service:
      raise ValueError(
          'Error authenticating sheets using provided JSON information'
      )
=======
        # Authorizes an httplib2.Http instance using service account credentials.
        creds = self.auth_service_creds(path_to_service_account_json_file,
                                        impersonation_email)
        service = build('sheets', 'v4', credentials=creds)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return sheets_service

  def auth_sheets_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str = None,
  ) -> discovery.Resource:
    """Creates Google sheets credentials based on a service account and email.

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address.

    Returns:
      Returns http object.
    """

    # Authorizes an httplib2.Http instance using service account credentials.
    creds = self.auth_service_creds(path_to_service_account_json_file,
                                    impersonation_email)
    service = build('sheets', 'v4', credentials=creds)

    return service
=======
        return service
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
