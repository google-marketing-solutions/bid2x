from typing import Any
from googleapiclient import discovery
from bid2x_spreadsheet import bid2x_spreadsheet
import auth.bid2x_auth as bid2x_auth

import bid2x_var
from bid2x_gtm import bid2x_gtm
from bid2x_dv import bid2x_dv


class bid2x_application():
    """
      Main object that handles all bid2x objects.

      Attributes:
          scopes (str): Scopes of the DV360/GTM APIs.
          service (Resource): Authenticated resource built for DV360/GTM API.
          api_name (str): Name of the script platform's API.
          api_version (str): Version of the script platform's API.
          sheet (bid2x_spreadsheet): Sheets resource of the referenced doc.
          _sheet_id (str): ID of the referenced sheet
          service_account_email (str): Service account used to authenticate
              between sheets and script platforms.
          json_auth_file (str): Client_secrets file to store service account
              credentials.
          auth (bid2x_auth): Auth object used to authenticate API services.
          platform_type (str): Platform that script is saved on (DV360 or GTM).
          platform_object (bid2x_gtm or bid2x_dv): Platform object of script.
          debug (bool): Debug flag.

      Methods:
          authenticate_service(self,
                               path_to_service_account_json_file,
                               impersonation_email,
                               service_type):
                Authenticates credentials and returns resource for
                service type.
          start_service(self): Creates the script's platform object.
          run_script(self): Starts the script creation and
                            modification process.
          top_level_copy(self, source): Copies all variable settings
              from config file to the object.
    """
    scopes: str

    service = None
    api_name: str
    api_version: str

    sheet: bid2x_spreadsheet
    _sheet_id: str

    # credentials settings
    service_account_email: str
    json_auth_file: str
    auth: bid2x_auth  # Used for authenticating different platforms

    # platform settings (DV360, GTM)
    platform_type: str
    platform_object = None

    debug: bool

    def __init__(self,
                scopes: str,
                api_name: str,
                api_version: str,
                sheet_id: str,
                auth_file: str,
                platform_type: str):

        self.scopes = scopes
        self.api_name = api_name
        self.api_version = api_version
        self.platform_type = platform_type
        self.service = None
        self._sheet_id = sheet_id
        self.json_auth_file = auth_file
        self.service_account_email = bid2x_var.SERVICE_ACCOUNT_EMAIL

        # Create blank GTM or DV bid2x object first
        if platform_type:
            print(f'init bid2x_application{platform_type}')
            if platform_type == bid2x_var.PlatformType.GTM.value:
                self.platform_object = bid2x_gtm(None, self.debug)
            elif platform_type == bid2x_var.PlatformType.DV.value:
                self.platform_object = bid2x_dv(None, self.debug)
            else:
                raise ValueError(f'Invalid platform type value: {platform_type}')


        self.sheet = bid2x_spreadsheet(sheet_id,auth_file)
        self.auth = bid2x_auth.bid2x_auth(scopes=scopes,
                                          api_name=api_name,
                                          api_version=api_version)
        self.json_auth_file = None

        self.debug = False


    def __str__(self)->str:
        """Override str method for this object to return a sensible string
          showing the object's main properties.
        Args:
          None
        Returns:
          A formatted string containing a formatted list of object properties.
        """
        return_str = (
          f'platform_type: {self.platform_type}\n'
          f'api_name: {self.api_name}\n'
          f'api_version: {self.api_version}\n'
          f'scopes: {self.scopes}\n'
          f'service_account_email: {self.service_account_email}\n'
          f'service: {self.service}\n'
          f'debug: {self.debug}\n'
          f'------------------------\n'
          f'Sheet Object:{self.sheet}\n'
          f'------------------------\n'
          f'Platform Object: {self.platform_object}\n')

        return return_str

    def __getstate__(self):
        state = self.__dict__.copy()  # Start with all attributes.
        del state['service']          # Remove the service attribute.
        return state                  # Return the modified state dictionary.

    def authenticate_service(self,
                             path_to_service_account_json_file: str,
                             impersonation_email: str = None,
                             service_type:str=None) -> discovery.Resource:
        """Creates authentication credentials based on a service account and email
          and saves it to bid2x_application.

        Args:
          path_to_service_account_json_file: file downloaded from GCP.
          impersonation_email: service account email address.

        Returns:
          Returns http object.
        """

        if service_type == bid2x_var.PlatformType.GTM.value:
            self.service = self.auth.auth_gtm_service(
                path_to_service_account_json_file,
                impersonation_email)
            service_output = self.service
        elif service_type == bid2x_var.PlatformType.DV.value:
            self.service = self.auth.auth_dv_service(
                path_to_service_account_json_file,
                impersonation_email)
            service_output = self.service
        elif service_type == bid2x_var.PlatformType.SHEETS.value:
            self.sheet.sheets_service = self.auth.auth_sheets(
                path_to_service_account_json_file,
                impersonation_email)

            service_output = self.sheet.sheets_service
            if self.sheet:
                print(f'Sheet is here: {self.sheet.sheet_id}, '
                      f'{self.sheet.sheet_url}')
            else:
                print('Sheet is not here')


        else:
            print(f'Error finding type of service to authenticate.  The '
                  f'current value is {service_type}')
            return False

        return service_output

    def start_service(self) -> None:
        """Creates the script's platform object based on the platform type.
        """
        if self.platform_type == bid2x_var.PlatformType.GTM.value:
            self.platform_object = bid2x_gtm(self.sheet,
                                             self.debug)
        if self.platform_type == bid2x_var.PlatformType.DV.value:
            self.platform_object = bid2x_dv(self.sheet,
                                            self.debug)

    def run_script(self) -> bool:
        """Creates new script and saves it to the appropriate platform.

        Args:
          None.

        Returns:
         True if script runs successfully.  False if it doesn't.
        """
        print(f'Platform Type {self.platform_type}')
        if self.platform_type == bid2x_var.PlatformType.GTM.value:
            print(f'Looking at platform_object {self.platform_object}')
            print(f'{dir(self.platform_object)}')
            self.platform_object.process_script(self.service)
        elif self.platform_type == bid2x_var.PlatformType.DV.value:
            print(f'Looking at platform_object {self.platform_object}')
            self.platform_object.process_script(self.service)
        else:
            return False

        return True

    def top_level_copy(self, source:Any)->None:
        """Copies all config file settings to this object and all
        associated objects.

        Args:
          source: The config file opened and decoded into readable format.

        Returns:
          None.
        """
        self.scopes = source['scopes']
        self.api_name = source['api_name']
        self.api_version = source['api_version']
        self.platform_type = source['platform_type']
        self.service_account_email = source['service_account_email']
        self.json_auth_file = source['json_auth_file']
        self.debug = source['debug']

        print(f'{self.platform_type}, {self.platform_object}')

        self.platform_object.top_level_copy(source)
