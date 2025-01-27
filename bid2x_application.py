<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
"""BidToX - bid2x_application module.

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

  This module contains the bid2x_application class.  This class is the
  main object that is used to run the Bid2X system.  It contains references
  to all the other objects that are used by the system and provides methods
  to run the system.
"""
import enum

=======
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
from typing import Any
<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
=======
from googleapiclient import discovery
from bid2x_spreadsheet import bid2x_spreadsheet
import auth.bid2x_auth as bid2x_auth

import bid2x_var
from bid2x_gtm import bid2x_gtm
from bid2x_dv import bid2x_dv
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
from auth import bid2x_auth
from bid2x_dv import Bid2xDV
from bid2x_gtm import Bid2xGTM
from bid2x_spreadsheet import Bid2xSpreadsheet
import bid2x_var
from googleapiclient import discovery

Enum = enum.Enum
Bid2xAuth = bid2x_auth.Bid2xAuth


class Bid2xApplication():
  """The main object that is used to run the Bid2X system.

  This class is the
  main object that is used to run the Bid2X system.  It contains references
  to all the other objects that are used by the system and provides methods
  to run the system.
  """

  scopes: str
  service = None
  api_name: str
  api_version: str
  platform_type: str
  platform_object = None
  sheet: Bid2xSpreadsheet
  _sheet_id: str
  zone_array = list[Any]
  debug: bool
  auth: None

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
    self.service = None
    self.debug = False
    self.platform_type = platform_type
    # Establish connection to Sheets
    self.sheet = Bid2xSpreadsheet(sheet_id, auth_file)

    # Create product-specific auth object
    self.auth = Bid2xAuth.Bid2xAuth(scopes, api_name, api_version)

  def __str__(self)->str:
    """Override str method for this object to return a useful string.

    Args:
       None
    Returns:
       A formatted string containing a formatted list of object properties.
=======

class bid2x_application():
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
    """
<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return_str = (
        f'api_name: {self.api_name}\n' +
        f'api_version: {self.api_version}'+
        f'service: {self.service}\n'+
        f'scopes: {self.scopes}\n'+
        f'debug: {self.debug}\n'+
        '------------------------\n' +
        f'Sheet Object:{self.sheet}\n' +
        '------------------------\n' +
        f'Auth Object:{self.auth}\n' +
        '------------------------\n' +
        'Zones:\n'
    )
=======
      Main object that handles all bid2x objects.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    for zone in self.zone_array:
      return_str += str(zone) + '\n----------------------\n'
=======
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
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return return_str

  def __getstate__(self):
    """Creates a copy of the object's state without the service attribute.

    Args: None.

    Returns:
      Returns object without service attribute.
    """

    state = self.__dict__.copy()  # Start with all attributes.
    del state['service']  # Remove the service attribute.
    return state  # Return the modified state dictionary.

  def authenticate_service(
      self,
      path_to_service_account_json_file: str,
      impersonation_email: str = None,
      service_type: str = None,
  ) -> discovery.Resource:
    """Creates authentication credentials based on a service account.

    Args:
      path_to_service_account_json_file: file downloaded from GCP.
      impersonation_email: service account email address.
      service_type: The type of service to authenticate.

    Returns:
      Returns http object.
=======
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
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
    """
    scopes: str

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if service_type == bid2x_var.PlatformType.GTM.value:
      self.service = self.auth.auth_gtm_service(
          path_to_service_account_json_file, impersonation_email
      )
      service_output = self.service
    elif service_type == bid2x_var.PlatformType.DV.value:
      self.service = self.auth.auth_dv_service(
          path_to_service_account_json_file, impersonation_email
      )
      service_output = self.service
    elif service_type == bid2x_var.PlatformType.SHEETS.value:
      self.sheet.sheets_service = self.auth.auth_sheets(
          path_to_service_account_json_file, impersonation_email
      )
=======
    service = None
    api_name: str
    api_version: str
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
      service_output = self.sheet.sheets_service
      if self.sheet:
        print(f'Sheet is here: {self.sheet.sheet_id}, {self.sheet.sheet_url}')
      else:
        print('Sheet is not here')
=======
    sheet: bid2x_spreadsheet
    _sheet_id: str
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    else:
      print(
          'Error finding type of service to authenticate.  The '
          f'current value is {service_type}'
      )
      return False
=======
    # credentials settings
    service_account_email: str
    json_auth_file: str
    auth: bid2x_auth  # Used for authenticating different platforms
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

    # platform settings (DV360, GTM)
    platform_type: str
    platform_object = None

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def start_service(self) -> None:
    """Creates the script's platform object based on the platform type."""
    if self.platform_type == bid2x_var.PlatformType.GTM.value:
      self.platform_object = Bid2xGTM(self.sheet, self.debug)
    if self.platform_type == bid2x_var.PlatformType.DV.value:
      self.platform_object = Bid2xDV(self.sheet, self.debug)
=======
    debug: bool
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

    def __init__(self,
                scopes: str,
                api_name: str,
                api_version: str,
                sheet_id: str,
                auth_file: str,
                platform_type: str):

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args: None.
=======
        self.scopes = scopes
        self.api_name = api_name
        self.api_version = api_version
        self.platform_type = platform_type
        self.service = None
        self._sheet_id = sheet_id
        self.json_auth_file = auth_file
        self.service_account_email = bid2x_var.SERVICE_ACCOUNT_EMAIL
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

        # Create blank GTM or DV bid2x object first
        if platform_type:
            print(f'init bid2x_application{platform_type}')
            if platform_type == bid2x_var.PlatformType.GTM.value:
                self.platform_object = bid2x_gtm(None, self.debug)
            elif platform_type == bid2x_var.PlatformType.DV.value:
                self.platform_object = bid2x_dv(None, self.debug)
            else:
                raise ValueError(f'Invalid platform type value: {platform_type}')


<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def top_level_copy(self, source: Any) -> None:
    """Copies all config file settings to this object..
=======
        self.sheet = bid2x_spreadsheet(sheet_id,auth_file)
        self.auth = bid2x_auth.bid2x_auth(scopes=scopes,
                                          api_name=api_name,
                                          api_version=api_version)
        self.json_auth_file = None
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

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

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    self.platform_object.top_level_copy(source)

  def assign_vars_to_objects(self) -> None:
    """Copy default values from bid2x_var scope into the app object.

    """
    # Ensure that the 'sheet' property has been initialized and exists.
    if not hasattr(self, 'sheet'):
      # Sheet object not here - re-initing new one
      self.sheet = Bid2xSpreadsheet(bid2x_var.SPREADSHEET_KEY,
                                    bid2x_var.JSON_AUTH_FILE)

    # Sheet object exists for sure now ensure that sheet_id, sheet_url,
    # and debug settings are correct.
    self.sheet.sheet_id = bid2x_var.SPREADSHEET_KEY
    self.sheet.sheet_url = (
        'https://docs.google.com/spreadsheets/d'
        f'/{bid2x_var.SPREADSHEET_KEY}/edit'
    )
    self.sheet.debug = bid2x_var.DEBUG

    # Platform type for Bid2X instance
    self.platform_type = bid2x_var.PLATFORM_TYPE

    # Connection-related properties
    self.scopes = bid2x_var.API_SCOPES
    self.api_name = bid2x_var.API_NAME
    self.api_version = bid2x_var.API_VERSION

    self.debug = bid2x_var.DEBUG
    self.platform_object.debug = bid2x_var.DEBUG
    self.json_auth_file = bid2x_var.JSON_AUTH_FILE
    self.service_account_email = bid2x_var.SERVICE_ACCOUNT_EMAIL

    if self.platform_type == enum.PlatformType.GTM:
      # GTM related properties
      self.platform_object.gtm_account_id = bid2x_var.GTM_ACCOUNT_ID
      self.platform_object.gtm_container_id = bid2x_var.GTM_CONTAINER_ID
      self.platform_object.gtm_workspace_id = bid2x_var.GTM_WORKSPACE_ID
      self.platform_object.gtm_variable_id = bid2x_var.GTM_VARIABLE_ID

    if self.platform_type == enum.PlatformType.DV:
      # Initialize action-related properties
      self.platform_object.action_list_algos = bool(bid2x_var.ACTION_LIST_ALGOS)
      self.platform_object.action_list_scripts = bool(
          bid2x_var.ACTION_LIST_SCRIPTS
      )
      self.platform_object.action_create_algorithm = bool(
          bid2x_var.ACTION_CREATE_ALGORITHM
      )
      self.platform_object.action_update_spreadsheet = bool(
          bid2x_var.ACTION_UPDATE_SPREADSHEET
      )
      self.platform_object.action_remove_algorithm = bool(
          bid2x_var.ACTION_REMOVE_ALGORITHM
      )
      self.platform_object.action_update_scripts = bool(
          bid2x_var.ACTION_UPDATE_SCRIPTS
      )
      self.platform_object.action_test = bool(bid2x_var.ACTION_TEST)

      # Initialize all the rest of the properties
      self.platform_object.clear_onoff = bid2x_var.CLEAR_ONOFF
      self.sheet.clear_onoff = bid2x_var.CLEAR_ONOFF
      self.platform_object.defer_pattern = bid2x_var.DEFER_PATTERN
      self.platform_object.alternate_algorithm = bid2x_var.ALTERNATE_ALGORITHM
      self.platform_object.new_algo_name = bid2x_var.NEW_ALGO_NAME
      self.platform_object.new_algo_display_name = (
          bid2x_var.NEW_ALGO_DISPLAY_NAME
      )
      self.platform_object.line_item_name_pattern = (
          bid2x_var.LINE_ITEM_NAME_PATTERN
      )
      self.platform_object.cb_tmp_file_prefix = bid2x_var.CB_TMP_FILE_PREFIX
      self.platform_object.cb_last_update_file_prefix = (
          bid2x_var.CB_LAST_UPDATE_FILE_PREFIX
      )
      self.platform_object.partner_id = bid2x_var.PARTNER_ID
      self.platform_object.advertiser_id = bid2x_var.ADVERTISER_ID
      self.platform_object.cb_algo_id = bid2x_var.CB_ALGO_ID
      self.platform_object.zones_to_process = bid2x_var.ZONES_TO_PROCESS
      self.platform_object.floodlight_id_list = bid2x_var.FLOODLIGHT_ID_LIST
      self.platform_object.attr_model_id = bid2x_var.ATTR_MODEL_ID
      self.platform_object.bidding_factor_high = bid2x_var.BIDDING_FACTOR_HIGH
      self.platform_object.bidding_factor_low = bid2x_var.BIDDING_FACTOR_LOW
=======
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
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
