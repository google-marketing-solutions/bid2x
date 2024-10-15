from typing import Any
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery


class bid2x_auth():
    """
      Authentication for bid2x objects.

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

    service = None
    _api_name: str
    _api_version: str

    def __init__(self,
                 scopes: str,
                 api_name: str,
                 api_version: str):
        self._scopes = scopes
        self._api_name = api_name
        self._api_version = api_version

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

        # Load the service account credentials from the specified JSON keyfile.
        service_credentials = self.auth_service_creds(
          path_to_service_account_json_file,
          impersonation_email)

        # Build the GTM service object.
        if service_credentials:
            self.service = discovery.build( self._api_name,
                                            self._api_version,
                                            credentials=service_credentials)

        return self.service

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

        # Build a service object for interacting with the API.
        if dv_http_service:
            self.service = discovery.build(
                self._api_name,
                self._api_version,
                http=dv_http_service)
        else:
            raise ValueError("Error authenticating using provided JSON information")

        return self.service

    def auth_dv_service(self,
                        path_to_service_account_json_file: str,
                        impersonation_email: str=None) -> discovery.Resource:

        """Creates DV credentials based on a service account and email.

        Args:
          path_to_service_account_json_file: file downloaded from GCP
          impersonation_email: service account email address.

        Returns:
          Returns http object.
        """

        """Performs OAuth2 for a DV360 service using
        service account credentials."""

        # Load the service account credentials from the specified JSON keyfile.
        service_credentials = self.auth_service_creds(
            path_to_service_account_json_file,
            impersonation_email)

        discovery_url = (f'https://displayvideo.googleapis.com/$discovery'
                         f'/rest?version={self._api_version}')

        if service_credentials:
            self.service = discovery.build(self._api_name,
                                           self._api_version,
                                           credentials=service_credentials,
                                           discoveryServiceUrl=discovery_url)
        return self.service

    def auth_sheets(self, auth_file: str, auth_email_account: str=None) -> discovery.Resource:
        """Creates Google sheets credentials based on a service account and email.

        Args:
          auth_file: file downloaded from GCP
          auth_email_account: service account email address.

        Returns:
          Returns http object.

        Raises:
          ValueError: If authentication fails.
        """

        # Set up service object to talk to Google Sheets.
        sheets_service = self.auth_sheets_service(auth_file, auth_email_account)

        # Build a service object for interacting with the API.
        if not sheets_service:
            raise ValueError("Error authenticating sheets using provided JSON information")

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

        # Authorizes an httplib2.Http instance using service account credentials.
        creds = self.auth_service_creds(path_to_service_account_json_file,
                                        impersonation_email)
        service = build('sheets', 'v4', credentials=creds)

        return service
