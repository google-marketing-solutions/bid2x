<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
"""BidToX - bid2x_dv application module.

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

  This module contains the DV360-specific functionality for the BidToX
  application.  It contains the classes and functions that are used
  to interact with the DV360 API to create, update, and remove custom
  bidding scripts.
"""

=======
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
import inspect
import json

from typing import Any
<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
=======

import gspread
from pandas import DataFrame
from googleapiclient.errors import HttpError

from bid2x_platform import Platform
from bid2x_spreadsheet import bid2x_spreadsheet
import bid2x_var
import bid2x_util
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

from bid2x_platform import Platform
from bid2x_spreadsheet import Bid2xSpreadsheet
import bid2x_util
import bid2x_var
from googleapiclient import errors
import gspread
import pandas

HttpError = errors.HttpError
DataFrame = pandas.DataFrame


class Bid2xDV(Platform):
  """DV360 object for custom bidding script.

  Attributes:
    sheet (bid2x_spreadsheet): Reference data for bid factor and LIs.
    zone_array (list[Any]): Targeted index and LIs settings for each
        zone's (tab in sheet).
    action_list_algos(bool): Flag to list all algorithms for a
        given advertiser.
    action_list_scripts(bool): Flag to list all scripts for a
        given advertiser.
    action_create_algorithm(bool): Flag to create new custom bidding
        algorithm at partner level.
    action_update_spreadsheet(bool): Flag to update spreadsheet.
    action_remove_algorithm(bool): Flag to remove given algorithm.
    action_update_scripts(bool): Flag to update custom bidding
        script.
    action_test(bool): Flag to create CB script and upload to sheets.
    debug(bool): Flag for debug mode.
    clear_onoff(bool): Clean up custom bidding flag in sheet.
    defer_pattern(bool): Update script creation flag in sheets.
    alternate_algorithm(bool): Alt algo flag for each floodlight.
    new_algo_name(str): Custom Bidding algo name.
    new_algo_display_name(str): Custom Bidding algo display name.
    line_item_name_pattern(str): Pattern in LI to pickup for algo.
    cb_tmp_file_prefix(str): Temp locatiom for CB script.
    cb_last_update_file_prefix(str): Prefix for last updated script.
    partner_id(int): Partner ID for the custom bidding script.
    advertiser_id(int): Advertiser ID for the custom bidding script.
    cb_algo_id(int): Algo ID of the custom bidding script.
    service_account_email(str): Cloud Service Account E-mail.
    zones_to_process(str):Zones involved in the bidding script.
    floodlight_id_list(list[str]): List of Floodlight IDs involved
        in script.
    attr_model_id(int): Attribution Model ID for Floodlights.
    bidding_factor_high(int): Max bidding factor.
    bidding_factor_low(int): Min bidding factor.

  Methods:
    list_partner_algo_scripts (self,
                                service,
                                partner_id,
                                algorithm_id):
        Given a service connection to DV360, partner ID, and
        algorithm ID this function lists the scripts associated
        with that algorithm ID and returns them in JSON format.

    list_advertiser_algo_scripts(self,
                                service,
                                advertiser_id,
                                algorithm_id):
        Given a service connection to DV360, partner ID, and
        algorithm ID this function lists the scripts associated
        with that algorithm ID and returns them in JSON format.

    list_advertiser_algorithms(self,
                                service,
                                advertiser_id):
        Given a service connection to DV360 and an advertiser ID
        this function lists custom bidding algorithms associated
        with that advertiser and returns them in JSON format.

    list_partner_algorithms(self,
                            service,
                            partner_id):
        Given a service connection to DV360 and a partner ID
        this function lists custom bidding algorithms associated
        with that partner and returns them in JSON format.

    create_cb_algorithm_partner(self,
                                service,
                                advertiser_id,
                                partner_id,
                                cb_script_name,
                                cb_display_name):
        This function creates a partner-level custom bidding
        algorithm.

    create_cb_algorithm_advertiser(self,
                                    service,
                                    advertiser_id,
                                    cb_script_name,
                                    cb_display_name):
        This function creates an advertiser-level custom
        bidding algorithm.

    remove_cb_algorithm_partner(self,
                        service,
                        partner_id,
                        algorithm_id):
        This function removes a partner-level custom bidding
        algorithm.

    remove_cb_algorithm_advertiser(self,
                                    service,
                                    advertiser_id,
                                    algorithm_id):
        This function removes an advertiser-level custom bidding
        algorithm.

    read_cb_algorithm_by_id(self,
                            service,
                            advertiser_id,
                            algorithm_id):
        This function returns the most recently uploaded script
        for this algorithm.

    write_tmp_file(self, script, filename_with_path):
        This function writes a string to a file.

    read_last_upload_file(self, filename_with_path):
        This function reads the last uploaded file and returns it
        as a string.  If the file cannot be found then an empty
        string is returned.

    write_last_upload_file(self, filename_with_path, script):
        This function writes the last uploaded file.

    print_data_frame(self, input_df: DataFrame):
        Converts a dataframe to a string and prints it to stdout.

    generate_cb_script_max_of_conversion_counts (self, zone_string):
        Generate a Custom Bidding script based on Max conversion
        counts across a single sales zone.

    process_script(self, service):
        This function orchestrates the custom bidding change in DV360
        that adjusts bid multipliers for different line items by way
        of a new custom bidding script that is created and saved.

    top_level_copy(self, source): Copies all variable settings
        from config file to the object.
  """
  sheet: Bid2xSpreadsheet

  zone_array = list[Any]

  action_list_algos: bool
  action_list_scripts: bool
  action_create_algorithm: bool
  action_update_spreadsheet: bool
  action_remove_algorithm: bool
  action_update_scripts: bool
  action_test: bool

  debug: bool
  clear_onoff: bool             # Clean up custom bidding flag in sheet.
  defer_pattern: bool           # Update script creation flag in sheets.
  alternate_algorithm: bool     # Alt algo flag for each floodlight.

  new_algo_name: str            # Custom Bidding algo name.
  new_algo_display_name: str    # Custom Bidding algo display name.
  line_item_name_pattern: str   # Pattern in LI to pickup for algo.

  cb_tmp_file_prefix: str          # Temp locatiom for CB script.
  cb_last_update_file_prefix: str  # Prefix for last updated script.

  partner_id: int              # Partner ID for the custom bidding script.
  advertiser_id: int           # Advertiser ID for the custom bidding script.
  cb_algo_id: int              # Algo ID of the custom bidding script.
  service_account_email: str   # Cloud Service Account E-mail.

  zones_to_process: str          # Zones involved in the bidding script.
  floodlight_id_list: list[str]  # List of Floodlight IDs involved in script.
  attr_model_id: int             # Attribution Model ID for Floodlights.
  bidding_factor_high: int       # Max bidding factor.
  bidding_factor_low: int        # Min bidding factor.

  def __init__(self, sheet: Bid2xSpreadsheet, debug: bool) -> None:
    self.sheet = sheet

    self.zone_array = []

    # Set defaults for action values.
    self.action_list_algos = False
    self.action_list_scripts = False
    self.action_create_algorithm = False
    self.action_update_spreadsheet = False
    self.action_remove_algorithm = False
    self.action_update_scripts = False
    self.action_test = False

    self.debug = debug
    self.clear_onoff = True
    self.defer_pattern = False
    self.alternate_algorithm = False

    # Placeholder default value strings for initialization.
    self.new_algo_name = 'bid2inventory'
    self.new_algo_display_name = 'bid2inventory'
    self.line_item_name_pattern = 'bid-to-invenotry'
    self.cb_tmp_file_prefix = '/tmp/cb_script'
    self.cb_last_update_file_prefix = 'last_upload'
    self.service_account_email = 'bid2x@test.com'

    # Default values for some IDs set to 0 to be used as 'uninitialized'
    # value.
    self.partner_id = 0
    self.advertiser_id = 0
    self.cb_algo_id = 0

    self.floodlight_id_list = None

    # Placeholder name of 'c1' for campaign 1 as zones typically
    # map to campaign during use.
    self.zones_to_process = 'c1'
    self.attr_model_id = 0

    self.bidding_factor_high = bid2x_var.BIDDING_FACTOR_HIGH
    self.bidding_factor_low = bid2x_var.BIDDING_FACTOR_LOW

  def __str__(self)->str:
    """Override str method to return a sensible string.

    Args:
        None.
    Returns:
        A formatted string containing a formatted list of object properties.
    """
<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
=======
          DV360 object for custom bidding script.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return_str = (
        f'action_list_algos: {self.action_list_algos}\n'
        f'action_list_scripts: {self.action_list_scripts}\n'
        f'action_create_algorithm: {self.action_create_algorithm}\n'
        f'action_update_spreadsheet: {self.action_update_spreadsheet}\n'
        f'action_remove_algorithm: {self.action_remove_algorithm}\n'
        f'action_update_scripts: {self.action_update_scripts}\n'
        f'action_test: {self.action_test}\n'
        f'clear_onoff: {self.clear_onoff}\n'
        f'defer_pattern: {self.defer_pattern}\n'
        f'alternate_algorithm: {self.alternate_algorithm}\n'
        f'new_algo_name: {self.new_algo_name}\n'
        f'new_algo_display_name: {self.new_algo_display_name}\n'
        f'line_item_name_pattern: {self.line_item_name_pattern}\n'
        f'cb_tmp_file_prefix: {self.cb_tmp_file_prefix}\n'
        f'cb_last_update_file_prefix: {self.cb_last_update_file_prefix}\n'
        f'partner_id: {self.partner_id}\n'
        f'advertiser_id: {self.advertiser_id}\n'
        f'cb_algo_id: {self.cb_algo_id}\n'
        f'floodlight_id_list: {self.floodlight_id_list}\n'
        f'zones_to_process: {self.zones_to_process}\n'
        f'attr_model_id: {self.attr_model_id}\n'
        f'bidding_factor_high: {self.bidding_factor_high}\n'
        f'bidding_factor_low: {self.bidding_factor_low}\n'
        '------------------------\n'
        'Zones:\n'
    )
=======
          Attributes:
              sheet (bid2x_spreadsheet): Reference data for bid factor and LIs.
              zone_array (list[Any]): Targeted index and LIs settings for each
                  zone's (tab in sheet).
              action_list_algos(bool): Flag to list all algorithms for a
                  given advertiser.
              action_list_scripts(bool): Flag to list all scripts for a
                  given advertiser.
              action_create_algorithm(bool): Flag to create new custom bidding
                  algorithm at partner level.
              action_update_spreadsheet(bool): Flag to update spreadsheet.
              action_remove_algorithm(bool): Flag to remove given algorithm.
              action_update_scripts(bool): Flag to update custom bidding
                  script.
              action_test(bool): Flag to create CB script and upload to sheets.
              debug(bool): Flag for debug mode.
              clear_onoff(bool): Clean up custom bidding flag in sheet.
              defer_pattern(bool): Update script creation flag in sheets.
              alternate_algorithm(bool): Alt algo flag for each floodlight.
              new_algo_name(str): Custom Bidding algo name.
              new_algo_display_name(str): Custom Bidding algo display name.
              line_item_name_pattern(str): Pattern in LI to pickup for algo.
              cb_tmp_file_prefix(str): Temp locatiom for CB script.
              cb_last_update_file_prefix(str): Prefix for last updated script.
              partner_id(int): Partner ID for the custom bidding script.
              advertiser_id(int): Advertiser ID for the custom bidding script.
              cb_algo_id(int): Algo ID of the custom bidding script.
              service_account_email(str): Cloud Service Account E-mail.
              zones_to_process(str):Zones involved in the bidding script.
              floodlight_id_list(list[str]): List of Floodlight IDs involved
                  in script.
              attr_model_id(int): Attribution Model ID for Floodlights.
              bidding_factor_high(int): Max bidding factor.
              bidding_factor_low(int): Min bidding factor.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    for zone in self.zone_array:
      return_str += str(zone) + '\n----------------------\n'

    return return_str

  def list_partner_algo_scripts(
      self, service: Any, partner_id: int, algorithm_id: int
  ) -> Any:
    """Lists the scripts associated with an algorithm ID at the partner level.

    Args:
        service: an active service connection object to DV360.
        partner_id: the partner ID of the partner to get the custom bidding algo
          list for.
        algorithm_id: the algorithm ID from which to return the list of
          associated scripts.
=======
          Methods:
              list_partner_algo_scripts (self,
                                         service,
                                         partner_id,
                                         algorithm_id):
                  Given a service connection to DV360, partner ID, and
                  algorithm ID this function lists the scripts associated
                  with that algorithm ID and returns them in JSON format.
              list_advertiser_algo_scripts(self,
                                           service,
                                           advertiser_id,
                                           algorithm_id):
                  Given a service connection to DV360, partner ID, and
                  algorithm ID this function lists the scripts associated
                  with that algorithm ID and returns them in JSON format.
              list_advertiser_algorithms(self,
                                         service,
                                         advertiser_id):
                  Given a service connection to DV360 and an advertiser ID
                  this function lists custom bidding algorithms associated
                  with that advertiser and returns them in JSON format.
              list_partner_algorithms(self,
                                      service,
                                      partner_id):
                  Given a service connection to DV360 and a partner ID
                  this function lists custom bidding algorithms associated
                  with that partner and returns them in JSON format.
              create_cb_algorithm_partner(self,
                                          service,
                                          advertiser_id,
                                          partner_id,
                                          cb_script_name,
                                          cb_display_name):
                  This function creates a partner-level custom bidding
                  algorithm.
              create_cb_algorithm_advertiser(self,
                                             service,
                                             advertiser_id,
                                             cb_script_name,
                                             cb_display_name):
                  This function creates an advertiser-level custom
                  bidding algorithm.
              remove_cb_algorithm_partner(self,
                                    service,
                                    partner_id,
                                    algorithm_id):
                    This function removes a partner-level custom bidding
                    algorithm.
              remove_cb_algorithm_advertiser(self,
                                             service,
                                             advertiser_id,
                                             algorithm_id):
                    This function removes an advertiser-level custom bidding
                    algorithm.
              read_cb_algorithm_by_id(self,
                                      service,
                                      advertiser_id,
                                      algorithm_id):
                    This function returns the most recently uploaded script
                    for this algorithm.
              write_tmp_file(self, script, filename_with_path):
                  This function writes a string to a file.
              read_last_upload_file(self, filename_with_path):
                  This function reads the last uploaded file and returns it
                  as a string.  If the file cannot be found then an empty
                  string is returned.
              write_last_upload_file(self, filename_with_path, script):
                  This function writes the last uploaded file.
              print_data_frame(self, input_df: DataFrame):
                  Converts a dataframe to a string and prints it to stdout.
              generate_cb_script_max_of_conversion_counts (self, zone_string):
                  Generate a Custom Bidding script based on Max conversion
                  counts across a single sales zone.
              process_script(self, service):
                  This function orchestrates the custom bidding change in DV360
                  that adjusts bid multipliers for different line items by way
                  of a new custom bidding script that is created and saved.
              top_level_copy(self, source): Copies all variable settings
              from config file to the object.
    """
    sheet: bid2x_spreadsheet

    zone_array = list[Any]

    action_list_algos: bool
    action_list_scripts: bool
    action_create_algorithm: bool
    action_update_spreadsheet: bool
    action_remove_algorithm: bool
    action_update_scripts: bool
    action_test: bool

    debug: bool
    clear_onoff: bool             # Clean up custom bidding flag in sheet.
    defer_pattern: bool           # Update script creation flag in sheets.
    alternate_algorithm: bool     # Alt algo flag for each floodlight.

    new_algo_name: str            # Custom Bidding algo name.
    new_algo_display_name: str    # Custom Bidding algo display name.
    line_item_name_pattern: str   # Pattern in LI to pickup for algo.

    cb_tmp_file_prefix: str          # Temp locatiom for CB script.
    cb_last_update_file_prefix: str  # Prefix for last updated script.

    partner_id: int              # Partner ID for the custom bidding script.
    advertiser_id: int           # Advertiser ID for the custom bidding script.
    cb_algo_id: int              # Algo ID of the custom bidding script.
    service_account_email: str   # Cloud Service Account E-mail.

    zones_to_process: str         # Zones involved in the bidding script.
    floodlight_id_list: list[str] # List of Floodlight IDs involved in script.
    attr_model_id: int            # Attribution Model ID for Floodlights.
    bidding_factor_high: int      # Max bidding factor.
    bidding_factor_low: int       # Min bidding factor.

    def __init__(self, sheet: bid2x_spreadsheet, debug: bool) -> None:
        self.sheet = sheet

        self.zone_array = []

        # Set defaults for action values.
        self.action_list_algos = False
        self.action_list_scripts = False
        self.action_create_algorithm = False
        self.action_update_spreadsheet = False
        self.action_remove_algorithm = False
        self.action_update_scripts = False
        self.action_test = False

        self.debug = debug
        self.clear_onoff = True
        self.defer_pattern = False
        self.alternate_algorithm = False

        # Placeholder default value strings for initialization.
        self.new_algo_name = 'bid2inventory'
        self.new_algo_display_name = 'bid2inventory'
        self.line_item_name_pattern = 'bid-to-invenotry'
        self.cb_tmp_file_prefix = '/tmp/cb_script'
        self.cb_last_update_file_prefix = 'last_upload'
        self.service_account_email = 'bid2x@test.com'

        # Default values for some IDs set to 0 to be used as 'uninitialized'
        # value.
        self.partner_id = 0
        self.advertiser_id = 0
        self.cb_algo_id = 0

        self.floodlight_id_list = None

        # Placeholder name of 'c1' for campaign 1 as zones typically
        # map to campaign during use.
        self.zones_to_process = 'c1'
        self.attr_model_id = 0

        self.bidding_factor_high = bid2x_var.BIDDING_FACTOR_HIGH
        self.bidding_factor_low = bid2x_var.BIDDING_FACTOR_LOW

    def __str__(self)->str:
        """Override str method for this object to return a sensible string
            showing the object's main properties.
        Args:
            None.
        Returns:
            A formatted string containing a formatted list of object properties.
        """
        return_str = (
            f'action_list_algos: {self.action_list_algos}\n'
            f'action_list_scripts: {self.action_list_scripts}\n'
            f'action_create_algorithm: {self.action_create_algorithm}\n'
            f'action_update_spreadsheet: {self.action_update_spreadsheet}\n'
            f'action_remove_algorithm: {self.action_remove_algorithm}\n'
            f'action_update_scripts: {self.action_update_scripts}\n'
            f'action_test: {self.action_test}\n'
            f'clear_onoff: {self.clear_onoff}\n'
            f'defer_pattern: {self.defer_pattern}\n'
            f'alternate_algorithm: {self.alternate_algorithm}\n'
            f'new_algo_name: {self.new_algo_name}\n'
            f'new_algo_display_name: {self.new_algo_display_name}\n'
            f'line_item_name_pattern: {self.line_item_name_pattern}\n'
            f'cb_tmp_file_prefix: {self.cb_tmp_file_prefix}\n'
            f'cb_last_update_file_prefix: {self.cb_last_update_file_prefix}\n'
            f'partner_id: {self.partner_id}\n'
            f'advertiser_id: {self.advertiser_id}\n'
            f'cb_algo_id: {self.cb_algo_id}\n'
            f'floodlight_id_list: {self.floodlight_id_list}\n'
            f'zones_to_process: {self.zones_to_process}\n'
            f'attr_model_id: {self.attr_model_id}\n'
            f'bidding_factor_high: {self.bidding_factor_high}\n'
            f'bidding_factor_low: {self.bidding_factor_low}\n'
            f'------------------------\n'
            f'Zones:\n')

        for zone in self.zone_array:
            return_str += str(zone) + '\n----------------------\n'

        return return_str

    def list_partner_algo_scripts(self,
                                  service: Any,
                                  partner_id: int,
                                  algorithm_id: int) -> dict:
        """Given a service connection to DV360, partner ID, and
        algorithm ID this function lists the scripts associated with that
        algorithm ID and returns them in JSON format.

        Args:
            service: an active service connection object to DV360.
            partner_id: the partner ID of the partner to get the custom
                        bidding algo list for.
            algorithmID: the algorithm ID from which to return the list
                        of associated scripts.
        Returns:
            A list of the scipts in JSON format.
        """
        request = service.customBiddingAlgorithms().scripts().list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            partnerId=f'{partner_id}')
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
        return response

    def list_advertiser_algo_scripts(self,
                                     service: Any,
                                     advertiser_id: int,
                                     algorithm_id: int) -> dict:
        """Given a service connection to DV360, partner ID, and
        algorithm ID this function lists the scripts associated with that
        algorithm ID and returns them in JSON format.

        Args:
            service: an active service connection object to DV360
            partner: the partner ID of the partner to get the custom
                        bidding algo list for
            algorithmID: the algorithm ID from which to return the list
                        of associated scripts
        Returns:
            A list of the scipts in JSON format
        """
        request = service.customBiddingAlgorithms().scripts().list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            advertiserId=f'{advertiser_id}')
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
        return response

    def list_advertiser_algorithms(self,
                                   service: Any,
                                   advertiser_id: int) -> dict:
        """Given a service connection to DV360 and an advertiser ID
        this function lists custom bidding algorithms associated with that
        advertiser and returns them in JSON format.

        Args:
            service: an active service connection object to DV360.
            advertiser: the advertiser ID of the advertiser to get the custom
                        bidding algo list for.
        Returns:
            A list of the associated custom bidding algorithms in JSON format
        """
        request = service.customBiddingAlgorithms().list(
            advertiserId=advertiser_id)
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
        return response

    def list_partner_algorithms(self,
                                service: Any,
                                partner_id: int) -> dict:
        """Given a service connection to DV360 and a partner ID
        this function lists custom bidding algorithms associated with that
        partner and returns them in JSON format.

        Args:
          service: an active service connection object to DV360.
          partner: the partner ID of the partner to get the custom
                   bidding algo list for.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        A list of the scipts in JSON format.
    """
=======
        Returns:
            A list of the associated custom bidding algorithms in JSON format
        """
        request = service.customBiddingAlgorithms().list(
            partnerId=partner_id)
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    request_custom_bidding_scripts_partner = (
        service.customBiddingAlgorithms()
        .scripts()
        .list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            partnerId=f'{partner_id}',
        )
    )
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_custom_bidding_scripts = bid2x_util.google_dv_call(
        request_custom_bidding_scripts_partner, context
    )
    return response_custom_bidding_scripts
=======
        return response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def list_advertiser_algo_scripts(
      self, service: Any, advertiser_id: int, algorithm_id: int
  ) -> Any:
    """Lists scripts associated with an algorithm ID at the advertiser level.
=======
    def create_cb_algorithm_partner(self,
                                    service: Any,
                                    advertiser_id: int,
                                    partner_id: int,
                                    cb_script_name: str,
                                    cb_display_name: str) -> dict:
        """This function creates a partner-level custom bidding algorithm.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360
        advertiser_id: the ID of the advertiser to get the custom bidding algo
          list for
        algorithm_id: the algorithm ID from which to return the list of
          associated scripts
=======
        Args:
            service: an active service connection object to DV360.
            advertiserId: the advertiser ID to create the custom
                          bidding algo for.
            partnerId: the partnerId to create the custom bidding algorithm
                under.
        Returns:
            The DV360 response from creating the new custom
            bidding algorithm in JSON format.
        """
        # Create the Custom Bidding Model details object.
        custom_bidding_model_details = {
            'advertiserId': f'{advertiser_id}',
            'readinessState': 'READINESS_STATE_TRAINING',
            'suspensionState': 'SUSPENSION_STATE_UNSPECIFIED' }
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        A list of the scipts in JSON format
    """
=======
        # Create the main Custom Bidding Model object with the options as passed.
        # This object will create the Custom Bidding model at the partner level.
        custom_bidding_algorithm = {
            'name': cb_script_name,
            'displayName': cb_display_name,
            'entityStatus': 'ENTITY_STATUS_ACTIVE',
            'customBiddingAlgorithmType': 'SCRIPT_BASED',
            'sharedAdvertiserIds': [
              advertiser_id ],
            'modelDetails': [ custom_bidding_model_details ],
            'partnerId': f'{partner_id}' }
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    request_custom_bidding_scripts_advertiser = (
        service.customBiddingAlgorithms()
        .scripts()
        .list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            advertiserId=f'{advertiser_id}',
        )
    )
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_custom_bidding_scripts_advertiser = bid2x_util.google_dv_call(
        request_custom_bidding_scripts_advertiser, context
    )
    return response_custom_bidding_scripts_advertiser
=======
        # Create the appropriate request object.
        request = service.customBiddingAlgorithms().create(
            body=custom_bidding_algorithm)
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def list_advertiser_algorithms(
      self, service: Any, advertiser_id: int
  ) -> Any:
    """List custom bidding algorithms associated with an advertiser ID.
=======
        return response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        advertiser_id: the advertiser ID of the advertiser to get the custom
          bidding algo list for.
=======
    def create_cb_algorithm_advertiser(self,
                                       service: Any,
                                       advertiser_id: int,
                                       cb_script_name: str,
                                       cb_display_name: str) -> dict:
        """This function creates an advertiser-level custom bidding algorithm.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        A list of the associated custom bidding algorithms in JSON format
    """
    request_algos_advertiser = service.customBiddingAlgorithms().list(
        advertiserId=advertiser_id
    )
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_algos_advertiser = bid2x_util.google_dv_call(
        request_algos_advertiser, context
    )
    return response_algos_advertiser
=======
        Args:
            service: an active service connection object to DV360.
            advertiserId: the advertiser ID to create the custom
                          bidding algo for.
        Returns:
            The DV360 response from creating the new custom bidding
            algorithm in JSON format.
        """
        # Create the Custom Bidding Model details object.
        custom_bidding_model_details = {
            'advertiserId': f'{advertiser_id}',
            'readinessState': 'READINESS_STATE_TRAINING',
            'suspensionState': 'SUSPENSION_STATE_UNSPECIFIED' }
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def list_partner_algorithms(self, service: Any, partner_id: int) -> Any:
    """List custom bidding algorithms associated with a partner ID.
=======
        # Create the main Custom Bidding Model object with the options as passed.
        # This object will create the Custom Bidding model at the advertiser level.
        custom_bidding_algorithm = {
            'name': cb_script_name,
            'displayName': cb_display_name,
            'entityStatus': 'ENTITY_STATUS_ACTIVE',
            'customBiddingAlgorithmType': 'SCRIPT_BASED',
            'sharedAdvertiserIds': [
              advertiser_id ],
            'modelDetails': [ custom_bidding_model_details ],
            'advertiserId': f'{advertiser_id}' }
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
      service: an active service connection object to DV360.
      partner_id: the partner ID of the partner to get the custom bidding
        algorithm list for.
=======
        request = service.customBiddingAlgorithms().create(
            body=custom_bidding_algorithm)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        A list of the associated custom bidding algorithms in JSON format
    """
    request_algos_partner = service.customBiddingAlgorithms().list(
        partnerId=partner_id
    )
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_algos_partner = bid2x_util.google_dv_call(
        request_algos_partner, context
    )
    return response_algos_partner
=======
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
        return response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def create_cb_algorithm_partner(
      self,
      service: Any,
      advertiser_id: int,
      partner_id: int,
      cb_script_name: str,
      cb_display_name: str,
  ) -> Any:
    """This function creates a partner-level custom bidding algorithm.
=======
    def remove_cb_algorithm_partner(self,
                                    service: Any,
                                    partner_id: int,
                                    algorithm_id: int) -> dict:
        """This function removes a partner-level custom bidding algorithm.
        Args:
            service: an active service connection object to DV360.
            partnerId: the partner ID of the partner under which the C.B. algo
                      to remove currently lives.
        Returns:
            The DV360 response from deleting the custom bidding
            algorithm in JSON format.
        """
        entity_status = {
            'partnerId':f'{partner_id}',
            'entityStatus':'ENTITY_STATUS_ARCHIVED'}
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        advertiser_id: the advertiser ID to create the custom bidding algo for.
        partner_id: the partnerId to create the custom bidding algorithm under.
        cb_script_name: the name of the custom bidding script to create.
        cb_display_name: the display name of the custom bidding script to
          create.
=======
        request = service.customBiddingAlgorithms().patch(
            customBiddingAlgorithmId=f'{algorithm_id}',
            updateMask='entityStatus',
            body=entity_status)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        The DV360 response from creating the new custom
        bidding algorithm in JSON format.
    """
    # Create the Custom Bidding Model details object.
    custom_bidding_model_details = {
        'advertiserId': f'{advertiser_id}',
        'readinessState': 'READINESS_STATE_TRAINING',
        'suspensionState': 'SUSPENSION_STATE_UNSPECIFIED',
    }
=======
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Create the main Custom Bidding Model object with the options as passed.
    # This object will create the Custom Bidding model at the partner level.
    custom_bidding_algorithm = {
        'name': cb_script_name,
        'displayName': cb_display_name,
        'entityStatus': 'ENTITY_STATUS_ACTIVE',
        'customBiddingAlgorithmType': 'SCRIPT_BASED',
        'sharedAdvertiserIds': [advertiser_id],
        'modelDetails': [custom_bidding_model_details],
        'partnerId': f'{partner_id}'
    }
=======
        return response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Create the appropriate request object.
    request_create_cb_algo_partner = service.customBiddingAlgorithms().create(
        body=custom_bidding_algorithm
    )
=======
    def remove_cb_algorithm_advertiser(self,
                                       service: Any,
                                       advertiser_id: int,
                                       algorithm_id: int) -> dict:
        """This function removes an advertiser-level custom bidding algorithm.
        Args:
            service: an active service connection object to DV360.
            advertiserId: the ID of the advertiser under which the C.B. algo
                      to remove currently lives.
        Returns:
            The DV360 response from deleting the custom bidding
            algorithm in JSON format.
        """
        entity_status = {
            'advertiserId':f'{advertiser_id}',
            'entityStatus':'ENTITY_STATUS_ARCHIVED' }
        request = service.customBiddingAlgorithms().patch(
            customBiddingAlgorithmId=f'{algorithm_id}',
            updateMask='entityStatus',
            body=entity_status)
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Make the call to DV360 and return the response.
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_create_cb_algo_partner = bid2x_util.google_dv_call(
        request_create_cb_algo_partner, context
    )
    return response_create_cb_algo_partner
=======
        return response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def create_cb_algorithm_advertiser(
      self,
      service: Any,
      advertiser_id: int,
      cb_script_name: str,
      cb_display_name: str,
  ) -> Any:
    """This function creates an advertiser-level custom bidding algorithm.
=======
    def read_cb_algorithm_by_id(self,
                                service: Any,
                                advertiser_id: int,
                                algorithm_id: int) -> str:
        """This function returns the most recently uploaded script
        for this algorithm.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        advertiser_id: the advertiser ID to create the custom bidding algo for.
        cb_script_name: the name of the custom bidding script to create.
        cb_display_name: the display name of the custom bidding script to
          create.
=======
        Args:
            service: an active service connection object to DV360.
            advertiser_id: the ID of the advertiser under which the C.B. algo
                to remove currently lives.
            algorithm_id: ID of the algorithm to get the most recent script from.
        Returns:
            The most recent script as a string from the algorithm ID.
        """
        # Get the list of scripts associated with the passed CB Algorithm
        # (each algorithm keeps a list of all the scripts it has used
        # including those that have been replaced with a newer script)
        request = service.customBiddingAlgorithms().scripts().list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            advertiserId=f'{advertiser_id}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        The DV360 response from creating the new custom bidding
        algorithm in JSON format.
    """
    # Create the Custom Bidding Model details object.
    custom_bidding_model_details = {
        'advertiserId': f'{advertiser_id}',
        'readinessState': 'READINESS_STATE_TRAINING',
        'suspensionState': 'SUSPENSION_STATE_UNSPECIFIED'
    }
=======
        response = bid2x_util.google_dv_call(
            request,
            inspect.currentframe().f_code.co_name + '_1')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Create the main Custom Bidding Model object with the options as passed.
    # This object will create the Custom Bidding model at the advertiser level.
    custom_bidding_algorithm = {
        'name': cb_script_name,
        'displayName': cb_display_name,
        'entityStatus': 'ENTITY_STATUS_ACTIVE',
        'customBiddingAlgorithmType': 'SCRIPT_BASED',
        'sharedAdvertiserIds': [advertiser_id],
        'modelDetails': [custom_bidding_model_details],
        'advertiserId': f'{advertiser_id}',
    }
=======
        if self.debug:
            print(f'full response: {response}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    request_create_cb_algo_advertiser = (
        service.customBiddingAlgorithms().create(body=custom_bidding_algorithm)
    )
=======
        # The default sort order of the output above is by createTime DESC.
        # Find the FIRST element whose state = 'ACCEPTED' as that is the most
        # recent for our purposes.
        if 'customBiddingScripts' in response:
            scripts = response['customBiddingScripts']
        else:
            # no scripts found return empyty string
            return ''
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    responsecreate_cb_algo_advertiser = bid2x_util.google_dv_call(
        request_create_cb_algo_advertiser, context
    )
    return responsecreate_cb_algo_advertiser
=======
        latest_accepted_script = None
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def remove_cb_algorithm_partner(
      self, service: Any, partner_id: int, algorithm_id: int
  ) -> Any:
    """This function removes a partner-level custom bidding algorithm.
=======
        for script in scripts:
            if script['state'] == 'ACCEPTED':
                latest_accepted_script = script
                break
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        partner_id: the partner ID of the partner under which the C.B. algo to
          remove currently lives.
        algorithm_id: the algorithm ID of the algorithm to remove.
=======
        if not latest_accepted_script:
            print('No most recent algorithm')
            return ''
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        The DV360 response from deleting the custom bidding
        algorithm in JSON format.
    """
    entity_status = {
        'partnerId': f'{partner_id}',
        'entityStatus': 'ENTITY_STATUS_ARCHIVED',
    }
=======
        # At this point the script of interest is in the variable
        # latest_accepted_script
        latest_cb_upload_script_id = latest_accepted_script['customBiddingScriptId']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    request_remove_cb_algo_partner = service.customBiddingAlgorithms().patch(
        customBiddingAlgorithmId=f'{algorithm_id}',
        updateMask='entityStatus',
        body=entity_status,
    )
=======
        if self.debug:
            print(f'customBiddingScriptId = {latest_cb_upload_script_id}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_remove_cb_algo_partner = bid2x_util.google_dv_call(
        request_remove_cb_algo_partner, context
    )
    return response_remove_cb_algo_partner
=======
        # Get details on the selected script ID
        request2 = service.customBiddingAlgorithms().scripts().get(
            customBiddingAlgorithmId=f'{algorithm_id}',
            customBiddingScriptId=f'{latest_cb_upload_script_id}',
            advertiserId=f'{advertiser_id}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def remove_cb_algorithm_advertiser(
      self, service: Any, advertiser_id: int, algorithm_id: int
  ) -> Any:
    """This function removes an advertiser-level custom bidding algorithm.
=======
        response2 = bid2x_util.google_dv_call(
            request2,
            inspect.currentframe().f_code.co_name+'_2')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        advertiser_id: the ID of the advertiser under which the C.B. algo to
          remove currently lives.
        algorithm_id: the algorithm ID of the algorithm to remove.
=======
        # The previous response should return an associated 'resourceName'
        # that is the lookup path to the media object that is the actual
        # algorithm script
        # Get the fileID which is the resource name to request
        media_file_id = response2['script']['resourceName']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        The DV360 response from deleting the custom bidding
        algorithm in JSON format.
    """
    entity_status = {
        'advertiserId': f'{advertiser_id}',
        'entityStatus': 'ENTITY_STATUS_ARCHIVED',
    }
    request_remove_cb_algo_advertiser = service.customBiddingAlgorithms().patch(
        customBiddingAlgorithmId=f'{algorithm_id}',
        updateMask='entityStatus',
        body=entity_status,
    )
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function
    else:
      context = None
    response_remove_cb_algo_advertiser = bid2x_util.google_dv_call(
        request_remove_cb_algo_advertiser, context
    )
    return response_remove_cb_algo_advertiser
=======
        # Make the media request to download the script file from
        # DV360 based on the media path we learned in the last step.
        media_request = service.media().download(
            resourceName=f'{media_file_id}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def read_cb_algorithm_by_id(
      self, service: Any, advertiser_id: int, algorithm_id: int
  ) -> str:
    """Returns the text of the most recently uploaded script for this algorithm.
=======
        # The default ending parameter of service requests is '?alt=json'
        # and for media requests this MUST be changed.  Make this happen
        # by splitting the built request url at '?' and then tacking
        # on the necessary URL parameter
        media_request.uri = media_request.uri.split('?')[0] + '?alt=media'
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        service: an active service connection object to DV360.
        advertiser_id: the ID of the advertiser under which the C.B. algo to
          remove currently lives.
        algorithm_id: ID of the algorithm to get the most recent script from.
=======
        # Make the call to DV360 to get the media
        media_response = bid2x_util.google_dv_call(media_request,
            inspect.currentframe().f_code.co_name+'_3')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        The most recent script as a string from the algorithm ID.
    """
    # Get the list of scripts associated with the passed CB Algorithm
    # (each algorithm keeps a list of all the scripts it has used
    # including those that have been replaced with a newer script)
    request_read_single_cb_algo = (
        service.customBiddingAlgorithms()
        .scripts()
        .list(
            customBiddingAlgorithmId=f'{algorithm_id}',
            advertiserId=f'{advertiser_id}',
        )
    )
=======
        return media_response
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function + '_1'
    else:
      context = None
    response_read_single_cb_algo = bid2x_util.google_dv_call(
        request_read_single_cb_algo, context
    )
=======
    def write_tmp_file(self,
                       script: str,
                       filename_with_path: str) -> None:
        """This function writes a string to a file.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.debug:
      print(f'full response: {response_read_single_cb_algo}')
=======
        Args:
            script: The string to write to file.
            filenameWithPath: A string containing a path and filename capable
                of being 'written' by the executor of this script.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # The default sort order of the output above is by createTime DESC.
    # Find the FIRST element whose state = 'ACCEPTED' as that is the most
    # recent for our purposes.
    if 'customBiddingScripts' in response_read_single_cb_algo:
      scripts = response_read_single_cb_algo['customBiddingScripts']
    else:
      # no scripts found return empyty string
      return ''

    latest_accepted_script = None

    for script in scripts:
      if script['state'] == 'ACCEPTED':
        latest_accepted_script = script
        break

    if not latest_accepted_script:
      print('No most recent algorithm')
      return ''

    # At this point the script of interest is in the variable
    # latest_accepted_script
    latest_cb_upload_script_id = latest_accepted_script['customBiddingScriptId']

    if self.debug:
      print(f'customBiddingScriptId = {latest_cb_upload_script_id}')

    # Get details on the selected script ID
    request_cb_script_details = (
        service.customBiddingAlgorithms()
        .scripts()
        .get(
            customBiddingAlgorithmId=f'{algorithm_id}',
            customBiddingScriptId=f'{latest_cb_upload_script_id}',
            advertiserId=f'{advertiser_id}',
        )
    )

    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      context = stack[1].function + '_2'
    else:
      context = None
    response_cb_script_details = bid2x_util.google_dv_call(
        request_cb_script_details, context
    )

    # The previous response should return an associated 'resourceName'
    # that is the lookup path to the media object that is the actual
    # algorithm script
    # Get the fileID which is the resource name to request
    media_file_id = response_cb_script_details['script']['resourceName']

    # Make the media request to download the script file from
    # DV360 based on the media path we learned in the last step.
    request_media_file = service.media().download(
        resourceName=f'{media_file_id}')

    # The default ending parameter of service requests is '?alt=json'
    # and for media requests this MUST be changed.  Make this happen
    # by splitting the built request url at '?' and then tacking
    # on the necessary URL parameter
    request_media_file.uri = request_media_file.uri.split('?')[0] + '?alt=media'

    # Make the call to DV360 to get the media
    stack = inspect.stack()
    if len(stack) > 1:  # Check if there's at least one frame beyond current
      media_context = stack[1].function + '_3'
    else:
      media_context = None
    media_response = bid2x_util.google_dv_call(
        request_media_file, media_context
    )
    return media_response

  def write_tmp_file(self, script: str, filename_with_path: str) -> None:
    """This function writes a string to a file.

    Args:
        script: The string to write to file.
        filename_with_path: A string containing a path and filename capable of
          being 'written' by the executor of this script.

    Returns:
        None.
    """
    # Write temporary file to tmp location.
    try:
      fp = open(filename_with_path, 'w')
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error opening file: {e}')
      raise

    try:
      fp.write(script)
    except (IOError, OSError) as e:
      print(f'Error writing local file: {e}')

    try:
      fp.close()
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error closing file: {e}')
      raise

    if self.debug:
      print('Wrote custom bidding script to tmp file')

  def read_last_upload_file(self, filename_with_path: str) -> str:
    """This function reads the last uploaded file and returns it as a string.

    Args:
        filename_with_path: a string containing a full path to a file.

    Returns:
        The contents of the file or an empty string if the file cannot be found.
    """
    # Set the default return value of empty string.
    data = ''

    # Try to open the file.
    try:
      fp = open(filename_with_path, 'r')
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error opening last update file: {e}')
      # Clear error is file is not found or error
      pass
      fp = None

    if fp:
      try:
        data = fp.read()
      except (IOError, OSError) as e:
        print(f'Error reading local file: {e}')
        raise
=======
        Returns:
            None.
        """
        # Write temporary file to tmp location.
        try:
            fp = open(filename_with_path,'w')
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f'Error opening file: {e}')
            raise

        try:
            fp.write(script)
        except (IOError, OSError) as e:
            print(f'Error writing local file: {e}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if fp:
      try:
        fp.close()
      except (FileNotFoundError, PermissionError, OSError) as e:
        print(f'Error closing file: {e}')
        raise
=======
        try:
            fp.close()
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f'Error closing file: {e}')
            raise
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return data
=======
        if self.debug:
            print('Wrote custom bidding script to tmp file')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def write_last_upload_file(self,
                             filename_with_path: str,
                             script: str) -> bool:
    """This function writes the last uploaded file.
=======
    def read_last_upload_file(self,
                              filename_with_path: str) -> str:
        """This function reads the last uploaded file and
        returns it as a string.  If the file cannot be found
        then an empty string is returned.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        filename_with_path: full path to file to write script to.
        script: the script to write to file as a string.
=======
        Args:
            filename_with_path - a string containing a full path to a file.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        True on success, False otherwise.
    """
    # Try to open the file for write.
    try:
      fp = open(filename_with_path, 'w')
    except (FileNotFoundError, PermissionError, OSError) as e:
      print('Error opening last update ',
            f'file {filename_with_path} for write: {e}')
      return False
=======
        Returns:
            The contents of the file or an empty string if the file cannot be found.
        """
        # Set the default return value of empty string.
        data = ''
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    try:
      fp.write(script)
    except (IOError, OSError) as e:
      print(f'Error writing local file: {e}')
      return False
=======
        # Try to open the file.
        try:
            fp = open(filename_with_path,'r')
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f'Error opening last update file: {e}')
            # Clear error is file is not found or error
            pass
            fp = None
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    try:
      fp.close()
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error closing file: {e}')
      raise
=======
        if fp:
            try:
                data = fp.read()
            except (IOError, OSError) as e:
                print(f'Error reading local file: {e}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return True
=======
        try:
            fp.close()
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f'Error closing file: {e}')
            raise
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def print_data_frame(self,
                       input_df: DataFrame) -> None:
    """Converts a dataframe to a string and prints it to stdout.
=======
        return data
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        input_df: any dataframe.
=======
    def write_last_upload_file(self,
                               filename_with_path: str,
                               script: str) -> bool:
        """This function writes the last uploaded file.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        None.
    """
    if self.debug:
      print(input_df.to_string())
=======
        Args:
            filename_with_path - full path to file to write script to.
            script - the script to write to file as a string.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def generate_cb_script_max_of_conversion_counts(self,
                                                  zone_string: str) -> str:
    """Generate a Custom Bidding script using max conversion counts.
=======
        Returns:
            True on success, False otherwise.
        """
        # Try to open the file for write.
        try:
            fp = open(filename_with_path,'w')
        except (FileNotFoundError, PermissionError, OSError) as e:
            print( 'Error opening last update ',
                  f'file {filename_with_path} for write: {e}')
            return False
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
        zone_string: the name of the sales zone.  The associated Google
        Sheets workbook is expected to have a tab with the same name as
        this string.
=======
        try:
            fp.write(script)
        except (IOError, OSError) as e:
            print(f'Error writing local file: {e}')
            return False
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
        A fully formed custom bidding script suitable for upload to DV360.
    """
    list_of_dicts = []
=======
        try:
            fp.close()
        except (FileNotFoundError, PermissionError, OSError) as e:
            print(f'Error closing file: {e}')
            raise
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    try:
      ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(
          zone_string)
      list_of_dicts = ref.get_all_records()
    except gspread.exceptions.SpreadsheetNotFound:
      print('Error: Spreadsheet not found while.')
    except gspread.exceptions.WorksheetNotFound:
      print('Error: Worksheet not found.')
    except gspread.exceptions.APIError as e:
      print(f'Error connecting to worksheet for get_all_records(): {e}')
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected error occurred: {e}')
    except (ValueError, TypeError) as e:
      print(f'Error reading values from get_all_records(): {e}')
    except TimeoutError:
      print('''Request timed out while opening spreadsheet.
            Please check your network connection.''')
      raise  # Reraise the exception
=======
        return True
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if not self.alternate_algorithm:
      # If we are not using the alternate algorithm then we need to
      # create a function that uses max_aggregate.
      cust_bidding_function_string = 'return max_aggregate(['
    else:
      # If we are using the alternate algorithm then we need to
      # create a function that uses if statements.
      cust_bidding_function_string = ''
=======
    def print_data_frame(self,
                         input_df: DataFrame) -> None:
        """Converts a dataframe to a string and prints it to stdout.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    processed_line_items = []
    for row in list_of_dicts:
      # If the 'Generate Custom Bidding' column is set to 'Yes' then
      # we need to process this row.
      if row['Generate Custom Bidding'].lower() == 'yes':
        factor = row['Bidding Factor']
        line_item_id = row['Line Item ID']
=======
        Args:
            input_df: any dataframe.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Calculate a 'valid' bidding factor value within the
        # bounds of high/low settings.
        verified_factor = min(
            max(factor, self.bidding_factor_low),
            self.bidding_factor_high
            )
=======
        Returns:
            None.
        """
        if self.debug:
            print(input_df.to_string())
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Conduct checks on the retrieved values of factor and line_item_id
        # to ensure they are valid numbers.  The lineItemID must be an
        # integer and the factor should be a float in a sensible range
        # low >= BIDDING_FACTOR_LO (default 0.5) and
        # high <= BIDDING_FACTOR_HIGH (default 1000).
=======
    def generate_cb_script_max_of_conversion_counts (self,
                                                     zone_string: str) -> str:
        """Generate a Custom Bidding script based on Max conversion counts across
          a single sales zone.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        if bid2x_util.is_number(factor) and line_item_id:
=======
        Args:
            zone_string: the name of the sales zone.  The associated Google Sheets
              workbook is expected to have a tab with the same name as this string.
            test_run: Boolean indicating whether this custom bidding script generation
              call is a test run.  Test run output is sent to a different cell on the
              'CB_Scripts' tab in the associated Google Sheet.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
          # If the line item ID does not exist in our list of processed
          # line item IDs then add to the custom bidding function string
          # and add this ID to the list of processed items.
          if processed_line_items.count(row['Line Item ID']) == 0:

            if not self.alternate_algorithm:
              # Loop and create a separate line for each
              # floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                cust_bidding_function_string += (
                    f'\n  ([total_conversion_count('
                    f'{floodlight_id_item},'
                    f'{self.attr_model_id})>0, ')
                cust_bidding_function_string += (
                    f'line_item_id == {line_item_id}], ')
                cust_bidding_function_string += (
                    f'{verified_factor}),')
            else:
              # Loop and create a separate if construct for each
              # floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                if not processed_line_items:
                  conditional_prefix = ''
                else:
                  conditional_prefix = 'el'
=======
        Returns:
            A fully formed custom bidding script suitable for upload to DV360.
        """
        if self.debug:
            print('In generate_cb_script_max_of_conversion_counts() - sheet:',
                self.sheet.sheet_id)
            print('In generate_cb_script_max_of_conversion_counts() - zone_string:',
                zone_string)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
                cust_bidding_function_string += (
                    f'\n{conditional_prefix}if line_item_id == ' +
                    f'{line_item_id}:')
                cust_bidding_function_string += (
                    '\n  return total_conversion_count')
                cust_bidding_function_string += (
                    f'({floodlight_id_item},',
                    f'{self.attr_model_id}) * ')
                cust_bidding_function_string += f'{verified_factor}'
=======
        try:
            ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(
                zone_string)
            list_of_dicts = ref.get_all_records()
        except gspread.exceptions.SpreadsheetNotFound:
            print('Error: Spreadsheet not found while.')
        except gspread.exceptions.WorksheetNotFound:
            print('Error: Worksheet not found.')
        except gspread.exceptions.APIError as e:
            print(f'Error connecting to worksheet for get_all_records(): {e}')
        except gspread.exceptions.GSpreadException as e:
            print(f'An unexpected error occurred: {e}')
        except HttpError as err:
            # If the error is a rate limit or connection error,
            # wait and try again.
            if bid2x_util.is_recoverable_http_error(err.resp.status):
                time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
                ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(
                  zone_string)
            # For all other errors raise the exception
            else:
                print(f'Error with Sheets trying to open Sheet:{e}')
                raise
        except (ValueError, TypeError) as e:
            print(f'Error reading values from get_all_records(): {e}')
        except TimeoutError:
            print('''Request timed out while opening spreadsheet.
                  Please check your network connection.''')
            raise  # Reraise the exception
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
            # We have processed this line item id, add it to the
            # list of processed items.
            processed_line_items.append(row['Line Item ID'])
=======
        if self.debug:
            print('list_of_dicts[] active items returned from Sheets:')
            for item in list_of_dicts:
                if item['Generate Custom Bidding'].lower() == 'yes':
                    print(f'ID :{item["Line Item ID"]}, ',
                          f'Bidding Factor:{item["Bidding Factor"]}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Remove trailing comma as we're out of the for loop now so
    # no further lines.
    if not self.alternate_algorithm:
      for floodlight_id_item in self.floodlight_id_list:
        cust_bidding_function_string += (
            '\n  ([total_conversion_count('
            f'{floodlight_id_item},{self.attr_model_id})>0], '
        )
        cust_bidding_function_string += (
            f'{min(max(0.5, self.bidding_factor_low), self.bidding_factor_high)}),'
        )
=======
        if not self.alternate_algorithm:
            cust_bidding_function_string = 'return max_aggregate(['
        else:
            cust_bidding_function_string = ''
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
      # Remove final comma & insert close right square bracket and
      # close parenthasis to finalize array and function.
      cust_bidding_function_string = cust_bidding_function_string.rstrip(',')
      cust_bidding_function_string += '])'
    else:
      cust_bidding_function_string += '\nelse:\n  return 0'
=======
        conditional_prefix = ''
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.debug:
      print(f'length of processedLineItems: {len(processed_line_items)}')
=======
        processed_line_items = []
        for row in list_of_dicts:
            if row['Generate Custom Bidding'].lower() == 'yes':
                factor = row['Bidding Factor']
                line_item_id = row['Line Item ID']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if not processed_line_items:
      cust_bidding_function_string = 'return 0;'
=======
            # Calculate a 'valid' bidding factor value within the
            # bounds of high/low settings.
            verified_factor = min(
                max(factor,self.bidding_factor_low),
                self.bidding_factor_high)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return cust_bidding_function_string
=======
            # Conduct checks on the retrieved values of factor and line_item_id
            # to ensure they are valid numbers.  The lineItemID must be an
            # integer and the factor should be a float in a sensible range
            # low >= BIDDING_FACTOR_LO (default 0.5) and
            # high <= BIDDING_FACTOR_HIGH (default 1000).
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def process_script(self, service: Any) -> bool:
    """Orchestrates the custom bidding change in DV360.
=======
            if bid2x_util.is_number(factor) and line_item_id:
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
      service: a service object previously opened with the DV360 API.
=======
                # If the line item ID does not exist in our list of processed
                # line item IDs then add to the custom bidding function string
                # and add this ID to the list of processed items.
                if processed_line_items.count(row['Line Item ID']) == 0:
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
      True if process is a success, False otherwise.
    """
=======
                    if not self.alternate_algorithm:
                        # Loop and create a separate line for each floodlight in the list.
                        for floodlight_id_item in self.floodlight_id_list:
                            cust_bidding_function_string += (
                                f'\n  ([total_conversion_count('
                                f'{floodlight_id_item},'
                                f'{self.attr_model_id})>0, ')
                            cust_bidding_function_string += (
                                f'line_item_id == {line_item_id}], ')
                            cust_bidding_function_string += (
                                f'{verified_factor}),')
                    else:
                        # Loop and create a separate if construct for each
                        # floodlight in the list.
                        for floodlight_id_item in self.floodlight_id_list:
                            if len(processed_line_items) == 0:
                                conditional_prefix = ''
                            else:
                                conditional_prefix = 'el'
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.action_list_scripts:
      # Show advertiser level scripts for each initialized zone
      for zone in self.zone_array:
        print(f'Custom bidding scripts for zone {zone.name}',
              f' advertiser_id = {zone.advertiser_id}')
=======
                            cust_bidding_function_string += (
                                f'\n{conditional_prefix}if line_item_id == {line_item_id}:')
                            cust_bidding_function_string += (
                                 '\n  return total_conversion_count')
                            cust_bidding_function_string += (
                                f'({floodlight_id_item},{self.attr_model_id}) * ')
                            cust_bidding_function_string += f'{verified_factor}'
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        response = self.list_advertiser_algo_scripts(
            service,
            zone.advertiser_id,
            zone.algorithm_id)
=======
                    # We have processed this line item id, add it to the
                    # list of processed items.
                    processed_line_items.append(row['Line Item ID'])
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        json_pretty_print = json.dumps(response, indent=2)
        print(f'{json_pretty_print}')
=======
        # Remove trailing comma as we're out of the for loop now so
        # no further lines.
        if not self.alternate_algorithm:
            for floodlight_id_item in self.floodlight_id_list:
                cust_bidding_function_string += \
                    '\n  ([total_conversion_count(' + \
                    f'{floodlight_id_item},{self.attr_model_id})>0], '
                cust_bidding_function_string += \
                    f'{min(max(0.5,self.bidding_factor_low), self.bidding_factor_high)}),'

            # Remove final comma & insert close right square bracket and
            # close parenthasis to finalize array and function.
            cust_bidding_function_string = cust_bidding_function_string.rstrip(',')
            cust_bidding_function_string += '])'
        else:
            cust_bidding_function_string += '\nelse:\n  return 0'

        if self.debug:
            print(f'length of processedLineItems: {len(processed_line_items)}')

        if len(processed_line_items) == 0:
            cust_bidding_function_string = 'return 0;'

        return cust_bidding_function_string

    def process_script(self, service):
        """This function orchestrates the custom bidding change in DV360 that adjusts
        bid multipliers for different line items by way of a new custom bidding script
        that is created and saved.

        Args:
          service: a service object previously opened with the DV360 API.

        Returns:
          True if process is a success.  False otherwise.
        """

        if self.action_list_scripts:
            # Show advertiser level scripts for each initialized zone
            for zone in self.zone_array:
                print(f'Custom bidding scripts for zone {zone.name}',
                      f' advertiser_id = {zone.advertiser_id}')
                response = self.list_advertiser_algo_scripts(service,
                                                             zone.advertiser_id,
                                                             zone.algorithm_id)
                json_pretty_print = json.dumps(response, indent=2)
                print(f'{json_pretty_print}')

        if self.action_list_algos:
            # Show advertiser level algorithms for each initialized zone
            print( 'Advertiser level algorithms for advertiser ID ',
                  f'= {self.advertiser_id}')
            response = self.list_advertiser_algorithms(service,
                          self.advertiser_id)
            json_pretty_print = json.dumps(response, indent=2)
            print(f'{json_pretty_print}')

        if self.action_create_algorithm:
            # Create a new custom bidding algorithm from Partner level.
            print('Create new custom bidding algorithm for zone(s):')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.action_list_algos:
      # Show advertiser level algorithms for each initialized zone
      print('Advertiser level algorithms for advertiser ID ',
            f'= {self.advertiser_id}')
      response = self.list_advertiser_algorithms(service,
                                                 self.advertiser_id)
      json_pretty_print = json.dumps(response, indent=2)
      print(f'{json_pretty_print}')
=======
            for zone in self.zone_array:
                # Create CB Algorithm at the Advertiser level.
                algorithmName = self.new_algo_name + '_' + zone.name
                displayName = self.new_algo_display_name + '_' + zone.name
                print(f'New algorithm name: {displayName}')
                response = self.create_cb_algorithm_advertiser(service,
                                                               self.advertiser_id,
                                                               algorithmName,
                                                               displayName)
                if self.debug:
                    json_pretty_print = json.dumps(response, indent=2)
                    print(f'new custom bidding algorithm response = {json_pretty_print}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.action_create_algorithm:
      # Create a new custom bidding algorithm from Partner level.
      print('Create new custom bidding algorithm for zone(s):')
=======
        if self.action_remove_algorithm:
            # Remove an advertiser custom bidding algorithm by ID.
            print(f'Custom bidding algorithm id {self.cb_algo_id} will ',
                  'attempted to be deleted.')
            response = self.remove_cb_algorithm_advertiser(service,
                                                           self.advertiser_id,
                                                           self.cb_algo_id)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
      for zone in self.zone_array:
        # Create CB Algorithm at the Advertiser level.
        algorithm_name = self.new_algo_name + '_' + zone.name
        display_name = self.new_algo_display_name + '_' + zone.name
        print(f'New algorithm name: {display_name}')
        response = self.create_cb_algorithm_advertiser(
            service,
            self.advertiser_id,
            algorithm_name,
            display_name)
=======
            print(f'result of deletion attempt: {response}')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        if self.debug:
          json_pretty_print = json.dumps(response, indent=2)
          print('New custom bidding algorithm ',
                f'response = {json_pretty_print}')
=======
        if self.action_update_scripts:
            # Update the custom bidding scripts in DV360.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    if self.action_remove_algorithm:
      # Remove an advertiser custom bidding algorithm by ID.
      print(f'Custom bidding algorithm id {self.cb_algo_id} will ',
            'attempted to be deleted.')
      response = self.remove_cb_algorithm_advertiser(
          service,
          self.advertiser_id,
          self.cb_algo_id)
=======
            # Create custom bidding script for DV360 as a string - per sales zone.
            for zone in self.zone_array:
                # Go into Google Sheets and generate CB function per sales zone.
                custom_bidding_function_string = \
                    self.generate_cb_script_max_of_conversion_counts(zone.name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
      print(f'result of deletion attempt: {response}')

    if self.action_update_scripts:
      # Update the custom bidding scripts in DV360.

      # Create custom bidding script string for DV360, per sales zone.
      for zone in self.zone_array:
        # Go into Google Sheets and generate CB function per sales zone.
        custom_bidding_function_string = (
            self.generate_cb_script_max_of_conversion_counts(zone.name)
        )
=======
                if self.debug:
                    # Show the generated custom bidding script.
                    print('custom_bidding_function_string:\n',
                          f'{custom_bidding_function_string}\n')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        if self.debug:
          # Show the generated custom bidding script.
          print(
              'custom_bidding_function_string:\n',
              f'{custom_bidding_function_string}\n',
          )
=======
                # Get a list of line items this will affect.
                line_item_array = \
                    self.sheet.get_affected_line_items_from_sheet(zone.name)
                # Get the current algorithm directly from DV360
                custom_bidding_current_script = \
                    self.read_cb_algorithm_by_id(service,
                                                 self.advertiser_id,
                                                 zone.algorithm_id)
                if self.debug:
                    print(f'new c.b.script:***{custom_bidding_function_string}***')
                    print(f'current script:***{custom_bidding_current_script}***')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Get a list of line items this will affect.
        line_item_array = self.sheet.get_affected_line_items_from_sheet(
            zone.name
        )
        # Get the current algorithm directly from DV360
        custom_bidding_current_script = self.read_cb_algorithm_by_id(
            service, self.advertiser_id, zone.algorithm_id
        )
=======
                # Updating custom bidding scripts deals with Media objects -
                # similar to the handling of creatives.  These are typically
                # files on a local file system and it's easier to deal with
                # the uploading of a custom bidding script by placing it in
                # a temp file.  Build the tmp filename using the custom budding
                # (cb) tmp file prefix an underscore and then the zone name
                # along with a '.txt' suffix.  Once we check that the new CB
                # script is actually new the contents of the script will be
                # written to this filename.
                filename = self.cb_tmp_file_prefix + '_' + zone.name + '.txt'
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Updating custom bidding scripts deals with Media objects -
        # similar to the handling of creatives.  These are typically
        # files on a local file system and it's easier to deal with
        # the uploading of a custom bidding script by placing it in
        # a temp file.  Build the tmp filename using the custom budding
        # (cb) tmp file prefix an underscore and then the zone name
        # along with a '.txt' suffix.  Once we check that the new CB
        # script is actually new the contents of the script will be
        # written to this filename.
        filename = self.cb_tmp_file_prefix + '_' + zone.name + '.txt'
=======
                # Compare the new script and the previously uploaded script.
                if str(custom_bidding_function_string).strip() == \
                    str(custom_bidding_current_script).strip():
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Compare the new script and the previously uploaded script.
        if (
            str(custom_bidding_function_string).strip()
            == str(custom_bidding_current_script).strip()
        ):
=======
                    # The new script is the same as the old script, don't
                    # write to file and don't upload.  Just return False from
                    # this function.
                    print('New script is the same as the existing script; not uploading')
                    return False
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
          # The new script is the same as the old script, don't
          # write to file and don't upload.  Just return False from
          # this function.
          print(
              f'New script for {zone.name} is the same as the existing script;'
              ' not uploading'
          )
          return False
=======
                else:
                    print('New script is different from last ',
                          'uploaded script; uploading new version')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        else:
          print(
              f'New script for {zone.name} is different from last ',
              'uploaded script; uploading new version',
          )
=======
                    # Write new script to tmp filename.  Upload is from a tmp file.
                    self.write_last_upload_file(filename,custom_bidding_function_string)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
          # Write new script to tmp filename.  Upload is from a tmp file.
          self.write_last_upload_file(filename, custom_bidding_function_string)
=======
                    # Make call to update script in DV360 passing in filename containing
                    # new script.
                    update_result = zone.update_custom_bidding_scripts(
                        service,
                        zone.advertiser_id,
                        zone.algorithm_id,
                        filename,
                        line_item_array)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
          # Make call to update script in DV360 passing in filename containing
          # new script.
          update_result = zone.update_custom_bidding_scripts(
              service,
              zone.advertiser_id,
              zone.algorithm_id,
              filename,
              line_item_array)
=======
                    if not update_result:
                        print(f'Update of C.B. Script for zone {zone.name} failed.')
                    else:
                        print(f'Update of C.B. Script for zone {zone.name} succeeded.')
                        # Update of C.B. script was successful, update the Google
                        # Sheets spreadsheet tab named 'CB_Scripts'
                        self.sheet.update_cb_scripts_tab(
                            zone,
                            custom_bidding_function_string,
                            test_run=False)

        if self.action_test:
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
          if not update_result:
            print(f'Update of C.B. Script for zone {zone.name} failed.')
          else:
            print(f'Update of C.B. Script for zone {zone.name} succeeded.')
=======
            for zone in self.zone_array:
                # Generate the Custom Bidding Script.
                custom_bidding_string = \
                  self.generate_cb_script_max_of_conversion_counts(zone.name)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
            # Update of C.B. script was successful, update the Google
            # Sheets spreadsheet tab named 'CB_Scripts'
            self.sheet.update_cb_scripts_tab(
                zone, custom_bidding_function_string, test_run=False
            )

    if self.action_test:
      for zone in self.zone_array:
        # Generate the Custom Bidding Script.
        custom_bidding_string = (
            self.generate_cb_script_max_of_conversion_counts(zone.name)
        )
        print(f'1/27 custom_bidding_string:\n{custom_bidding_string}\n')
=======
                # Print the value of the script to the console - since this
                # runs typically as a Cloud Function then this will end up
                # in the logs.
                print(f'''rules for zone {zone.name}:\n
                    {custom_bidding_string}''')
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Print the value of the script to the console.
        if self.debug:
          print(f"""rules for zone {zone.name}:\n
                {custom_bidding_string}""")
=======
                # Write the Test Run out to the test column in the associated
                # Google Sheet in the tab 'CB_Scripts'
                self.sheet.update_cb_scripts_tab(
                    zone,
                    custom_bidding_string,
                    test_run=True)
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
        # Write the Test Run out to the test column in the associated
        # Google Sheet in the tab 'CB_Scripts'
        self.sheet.update_cb_scripts_tab(
            zone, custom_bidding_string, test_run=True
        )

    if self.action_update_spreadsheet:
      self.sheet.read_dv_line_items(
          service,
          self.line_item_name_pattern,
          self.zone_array,
          self.defer_pattern,
      )
=======
        if self.action_update_spreadsheet:
            self.sheet.read_dv_line_items (service,
                                           self.line_item_name_pattern,
                                           self.zone_array,
                                           self.defer_pattern)
        return True
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    return True
=======
    def top_level_copy(self, source:Any)->None:
        """Copies all config file DV360 settings to this object and all
        associated objects.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
  def top_level_copy(self, source: Any) -> None:
    """Copies all config file DV360 settings to this object.
=======
        Args:
          source: The config file opened and decoded into readable format.
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Args:
      source: The config file opened and decoded into readable format.
=======
        Returns:
          None.
        """
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    Returns:
      None.
    """
=======
        self.debug = source['debug']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    self.debug = source['debug']
=======
        # Set defaults for action values.
        self.action_list_algos = source['action_list_algos']
        self.action_list_scripts = source['action_list_scripts']
        self.action_create_algorithm = source['action_create_algorithm']
        self.action_update_spreadsheet = source['action_update_spreadsheet']
        self.action_remove_algorithm = source['action_remove_algorithm']
        self.action_update_scripts = source['action_update_scripts']
        self.action_test = source['action_test']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Set defaults for action values.
    self.action_list_algos = source['action_list_algos']
    self.action_list_scripts = source['action_list_scripts']
    self.action_create_algorithm = source['action_create_algorithm']
    self.action_update_spreadsheet = source['action_update_spreadsheet']
    self.action_remove_algorithm = source['action_remove_algorithm']
    self.action_update_scripts = source['action_update_scripts']
    self.action_test = source['action_test']
=======
        # Set defaults for other Booleans.
        self.clear_onoff = source['clear_onoff']
        self.defer_pattern = source['defer_pattern']
        self.alternate_algorithm = source['alternate_algorithm']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Set defaults for other Booleans.
    self.clear_onoff = source['clear_onoff']
    self.defer_pattern = source['defer_pattern']
    self.alternate_algorithm = source['alternate_algorithm']
=======
        # Placeholder default value strings for initialization.
        self.new_algo_name = source['new_algo_name']
        self.new_algo_display_name = source['new_algo_display_name']
        self.line_item_name_pattern = source['line_item_name_pattern']
        self.cb_tmp_file_prefix = source['cb_tmp_file_prefix']
        self.cb_last_update_file_prefix = source['cb_last_update_file_prefix']
        self.service_account_email = source['service_account_email']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Placeholder default value strings for initialization.
    self.new_algo_name = source['new_algo_name']
    self.new_algo_display_name = source['new_algo_display_name']
    self.line_item_name_pattern = source['line_item_name_pattern']
    self.cb_tmp_file_prefix = source['cb_tmp_file_prefix']
    self.cb_last_update_file_prefix = source['cb_last_update_file_prefix']
    self.service_account_email = source['service_account_email']
=======
        # Default values for some IDs set to 0 to be used as 'uninitialized'
        # value.
        self.partner_id = source['partner_id']
        self.advertiser_id = source['advertiser_id']
        self.cb_algo_id = source['cb_algo_id']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Default values for some IDs set to 0 to be used as 'uninitialized'
    # value.
    self.partner_id = source['partner_id']
    self.advertiser_id = source['advertiser_id']
    self.cb_algo_id = source['cb_algo_id']
=======
        self.floodlight_id_list = source['floodlight_id_list']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    self.floodlight_id_list = source['floodlight_id_list']
=======
        # Placeholder name of 'c1' for campaign 1 as zones typically
        # map to campaign during use.
        self.zones_to_process = source['zones_to_process']
        self.attr_model_id = source['attr_model_id']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )

<<<<<<< PATCH SET (39220e DV + GTM/SA including formatting for PyLinter)
    # Placeholder name of 'c1' for campaign 1 as zones typically
    # map to campaign during use.
    self.zones_to_process = source['zones_to_process']
    self.attr_model_id = source['attr_model_id']

    self.bidding_factor_high = source['bidding_factor_high']
    self.bidding_factor_low = source['bidding_factor_low']
=======
        self.bidding_factor_high = source['bidding_factor_high']
        self.bidding_factor_low = source['bidding_factor_low']
>>>>>>> BASE      (015c88 Extended code to modify bidding multiplier script for DV360 )
