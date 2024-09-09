import time
import gspread
import inspect
import httplib2

from typing import Any
from pandas import DataFrame
from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from http import HTTPStatus

from bid2x_spreadsheet import bid2x_spreadsheet
from bid2x_model import bid2x_model
from bid2x_util import *
import bid2x_var

class bid2x_application():

  trix: str
  scopes: str

  dv_service = None
  dv_api_name: str
  dv_api_version: str

  sheet: bid2x_spreadsheet
  zone_array = list[bid2x_model]

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

  json_auth_file: str
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

  def __init__(self,
               trix: str,
               scopes: str,
               dv_api_name: str,
               dv_api_version: str,
               sheet_id: str,
               auth_file: str):

    self.trix = trix
    self.scopes = scopes
    self.dv_api_name = dv_api_name
    self.dv_api_version = dv_api_version
    self.dv_service = None

    self.sheet = bid2x_spreadsheet(sheet_id,auth_file)
    self.zone_array = []

    # Set defaults for action values.
    self.action_list_algos = False
    self.action_list_scripts = False
    self.action_create_algorithm = False
    self.action_update_spreadsheet = False
    self.action_remove_algorithm = False
    self.action_update_scripts = False
    self.action_test = False

    # Set defaults for other Booleans.
    self.debug = False
    self.clear_onoff = True
    self.defer_pattern = False
    self.alternate_algorithm = False

    # Placeholder default value strings for initialization.
    self.new_algo_name = "bid2inventory"
    self.new_algo_display_name = "bid2inventory"
    self.line_item_name_pattern = "bid-to-invenotry"
    self.cb_tmp_file_prefix = '/tmp/cb_script'
    self.cb_last_update_file_prefix = 'last_upload'
    self.service_account_email = 'bid2x@test.com'

    # Default values for some IDs set to 0 to be used as 'uninitialized'
    # value.
    self.partner_id = 0
    self.advertiser_id = 0
    self.cb_algo_id = 0

    self.json_auth_file = None
    self.floodlight_id_list = None

    # Placeholder name of 'c1' for campaign 1 as zones typically
    # map to campaign during use.
    self.zones_to_process = 'c1'
    self.attr_model_id = 0

    self.bidding_factor_high = bid2x_var.BIDDING_FACTOR_HIGH
    self.bidding_factor_low = bid2x_var.BIDDING_FACTOR_LOW

  def __str__(self) -> None:
    print(f'trix: {self.trix}')
    print(f'dv_api_name: {self.dv_api_name}')
    print(f'dv_api_version: {self.dv_api_version}')

  def set_trix(self,str_trix: str) -> None:
    self.trix = str_trix

  def set_scopes (self,str_scopes: str) -> None:
    self.scopes = str_scopes

  def auth_dv(self, auth_file: str, auth_email_account: str) -> Any:
    """Top level function for auth'ing to DV360
    Args:
      auth_file: An authentication file in json format
      auth_email_account: The email account (typically a service account)
        under which the auth file is to be used
    Returns:
      Returns True if able to create a good .dv_service object
      within this class, otherwise it returns False.
    """
    dv_http_service = self.auth_dv_service(auth_file,
                                           auth_email_account)

    # Build a service object for interacting with the API.
    if dv_http_service:
        self.dv_service = discovery.build(
          self.dv_api_name,
          self.dv_api_version,
          http=dv_http_service) 
    else:
        print(f"Error authenticating using provided JSON information")
        return False

    return self.dv_service

  def auth_dv_service(self,
                      path_to_service_account_json_file: str,
                      impersonation_email: str) -> Any:

    """Creates DV credentials based on a service account and email

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address

    Returns:
      Returns http object
    """

    """Performs OAuth2 for a DV360 service using 
    service account credentials."""

    # Load the service account credentials from the specified JSON keyfile.
    service_credentials = ServiceAccountCredentials.from_json_keyfile_name(
      path_to_service_account_json_file,
      scopes=self.scopes)

    # Configure impersonation (if applicable).
    if impersonation_email:
        service_credentials = service_credentials.create_delegated(
          impersonation_email)

    discovery_url = f'https://displayvideo.googleapis.com/$discovery' + \
      f'/rest?version={self.dv_api_version}'

    if service_credentials:
      self.dv_service = discovery.build(self.dv_api_name,
                                        self.dv_api_version,
                                        credentials=service_credentials,
                                        discoveryServiceUrl=discovery_url)
    return self.dv_service


  def auth_sheets(self, auth_file: str, auth_email_account: str) -> Any:
    # Set up service object to talk to Google Sheets.
    sheets_service = self.auth_sheets_service(auth_file, auth_email_account)

    # Build a service object for interacting with the API.
    if not sheets_service:
        print(f"Error authenticating sheets using provided JSON information")
        return False
    else:
       self.sheet.sheets_service = sheets_service

    return sheets_service

  def auth_sheets_service(self,
                          path_to_service_account_json_file: str,
                          impersonation_email: str) -> Any:

    """Authorizes an httplib2.Http instance
    using service account credentials."""

    # Load the service account credentials from the specified JSON keyfile.
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        path_to_service_account_json_file,
        scopes=self.scopes)
    # Configure impersonation (if applicable).
    if impersonation_email:
        credentials = creds.create_delegated(impersonation_email)
    # Use the credentials to authorize an httplib2.Http instance.
    service = build('sheets', 'v4', credentials=creds)

    return service

  def list_partner_algo_scripts(self,
                                service: Any,
                                partner_id: int,
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
      partnerId=f'{partner_id}')
    response = google_dv_call(request,
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
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def list_advertiser_algorithms(self,
                                 service: Any,
                                 advertiser_id: int) -> dict:
    """Given a service connection to DV360 and an advertiser ID
    this function lists custom bidding algorithms associated with that
    advertiser and returns them in JSON format.
    Args:
      service: an active service connection object to DV360
      advertiser: the advertiser ID of the advertiser to get the custom
                  bidding algo list for
    Returns:
      A list of the associated custom bidding algorithms in JSON format
    """
    request = service.customBiddingAlgorithms().list(
      advertiserId=advertiser_id)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def list_partner_algorithms(self,
                              service: Any,
                              partner_id: int) -> dict:
    """Given a service connection to DV360 and a partner ID
    this function lists custom bidding algorithms associated with that
    partner and returns them in JSON format.
    Args:
      service: an active service connection object to DV360
      partner: the partner ID of the partner to get the custom
                  bidding algo list for
    Returns:
      A list of the associated custom bidding algorithms in JSON format
    """
    request = service.customBiddingAlgorithms().list(
      partnerId=partner_id)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def create_cb_algorithm_partner(self,
                                  service: Any,
                                  advertiser_id: int,
                                  partner_id: int,
                                  cb_script_name: str,
                                  cb_display_name: str) -> dict:
    """This function creates a partner-level custom bidding algorithm.
    Args:
      service: an active service connection object to DV360
      advertiserId: the advertiser ID to create the custom
                    bidding algo for
      partnerId: the partnerId to create the custom bidding algorithm under
    Returns:
      The DV360 response from creating the new custom
      bidding algorithm in JSON format.
    """
    # Create the Custom Bidding Model details object.
    custom_bidding_model_details = {
      "advertiserId": f'{advertiser_id}',
      "readinessState": 'READINESS_STATE_TRAINING',
      "suspensionState": 'SUSPENSION_STATE_UNSPECIFIED' }
    # Create the main Custom Bidding Model object with the options as passed.
    # This object will create the Custom Bidding model at the partner level.
    custom_bidding_algorithm = {
      "name": cb_script_name,
      "displayName": cb_display_name,
      "entityStatus": 'ENTITY_STATUS_ACTIVE',
      "customBiddingAlgorithmType": 'SCRIPT_BASED',
      "sharedAdvertiserIds": [
        advertiser_id ],
      "modelDetails": [ custom_bidding_model_details ],
      "partnerId": f'{partner_id}' }
    # Create the appropriate request object.
    request = service.customBiddingAlgorithms().create(
      body=custom_bidding_algorithm)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def create_cb_algorithm_advertiser(self,
                                     service: Any,
                                     advertiser_id: int,
                                     cb_script_name: str,
                                     cb_display_name: str) -> dict:
    """This function creates an advertiser-level custom bidding algorithm.
    Args:
      service: an active service connection object to DV360
      advertiserId: the advertiser ID to create the custom
                    bidding algo for.
    Returns:
      The DV360 response from creating the new custom bidding
      algorithm in JSON format.
    """
    # Create the Custom Bidding Model details object.
    custom_bidding_model_details = {
      "advertiserId": f'{advertiser_id}',
      "readinessState": 'READINESS_STATE_TRAINING',
      "suspensionState": 'SUSPENSION_STATE_UNSPECIFIED' }
    # Create the main Custom Bidding Model object with the options as passed.
    # This object will create the Custom Bidding model at the advertiser level.
    custom_bidding_algorithm = {
      "name": cb_script_name,
      "displayName": cb_display_name,
      "entityStatus": 'ENTITY_STATUS_ACTIVE',
      "customBiddingAlgorithmType": 'SCRIPT_BASED',
      "sharedAdvertiserIds": [
        advertiser_id ],
      "modelDetails": [ custom_bidding_model_details ],
      "advertiserId": f'{advertiser_id}' }
    request = service.customBiddingAlgorithms().create(
      body=custom_bidding_algorithm)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def remove_cb_algorithm_partner(self,
                                  service: Any,
                                  partner_id: int,
                                  algorithm_id: int) -> dict:
    """This function removes a partner-level custom bidding algorithm
    Args:
      service: an active service connection object to DV360
      partnerId: the partner ID of the partner under which the C.B. algo
                to remove currently lives
    Returns:
      The DV360 response from deleting the custom bidding
      algorithm in JSON format
    """
    entity_status = {
      'partnerId':f'{partner_id}',
      'entityStatus':'ENTITY_STATUS_ARCHIVED'}
    request = service.customBiddingAlgorithms().patch(
      customBiddingAlgorithmId=f'{algorithm_id}',
      updateMask="entityStatus",
      body=entity_status)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def remove_cb_algorithm_advertiser(self,
                                     service: Any,
                                     advertiser_id: int,
                                     algorithm_id: int) -> dict:
    """This function removes an advertiser-level custom bidding algorithm
    Args:
      service: an active service connection object to DV360
      advertiserId: the ID of the advertiser under which the C.B. algo
                to remove currently lives
    Returns:
      The DV360 response from deleting the custom bidding
      algorithm in JSON format.
    """
    entity_status = {
      'advertiserId':f'{advertiser_id}',
      'entityStatus':'ENTITY_STATUS_ARCHIVED' }
    request = service.customBiddingAlgorithms().patch(
      customBiddingAlgorithmId=f'{algorithm_id}',
      updateMask="entityStatus",
      body=entity_status)
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name)
    return response

  def read_cb_algorithm_by_id(self,
                              service: Any,
                              advertiser_id: int,
                              algorithm_id: int) -> str:
    """This function returns the most recently uploaded script
    for this algorithm.
    Args:
      service: an active service connection object to DV360
      advertiser_id: the ID of the advertiser under which the C.B. algo
                to remove currently lives
      algorithm_id: ID of the algorithm to get the most recent script from
    Returns:
      The most recent script as a string from the algorithm ID
    """
    # Get the list of scripts associated with the passed CB Algorithm
    # (each algorithm keeps a list of all the scripts it has used
    # including those that have been replaced with a newer script)
    request = service.customBiddingAlgorithms().scripts().list(
      customBiddingAlgorithmId=f'{algorithm_id}',
      advertiserId=f'{advertiser_id}')
    response = google_dv_call(request,
                              inspect.currentframe().f_code.co_name + "_1")
    if self.debug:
      print(f'full response: {response}')

    # The default sort order of the output above is by createTime DESC.
    # Find the FIRST element whose state = 'ACCEPTED' as that is the most
    # recent for our purposes.
    if 'customBiddingScripts' in response:
      scripts = response['customBiddingScripts']
    else:
      # no scripts found return empyty string
      return ""
    latest_accepted_script = None
    for script in scripts:
      if script['state'] == 'ACCEPTED':
        latest_accepted_script = script
        break
    if not latest_accepted_script:
      print("No most recent algorithm")
      return ""

    # At this point the script of interest is in the variable
    # latest_accepted_script
    latest_cb_upload_script_id = latest_accepted_script['customBiddingScriptId']
    if self.debug:
      print(f'customBiddingScriptId = {latest_cb_upload_script_id}')

    # Get details on the selected script ID
    request2 = service.customBiddingAlgorithms().scripts().get(
      customBiddingAlgorithmId=f'{algorithm_id}',
      customBiddingScriptId=f'{latest_cb_upload_script_id}',
      advertiserId=f'{advertiser_id}')
    response2 = google_dv_call(request2,
                               inspect.currentframe().f_code.co_name+"_2")

    # The previous response should return an associated 'resourceName'
    # that is the lookup path to the media object that is the actual
    # algorithm script
    # Get the fileID which is the resource name to request
    media_file_id = response2['script']['resourceName']
    # Make the media request to download the script file from
    # DV360 based on the media path we learned in the last step.
    media_request = service.media().download(
      resourceName=f'{media_file_id}')
    # The default ending parameter of service requests is '?alt=json'
    # and for media requests this MUST be changed.  Make this happen
    # by splitting the built request url at '?' and then tacking
    # on the necessary URL parameter
    media_request.uri = media_request.uri.split("?")[0] + "?alt=media"
    # Make the call to DV360 to get the media
    media_response = google_dv_call(media_request,
                                    inspect.currentframe().f_code.co_name+"_3")

    return media_response

  def write_tmp_file(self,
                     script: str,
                     filename_with_path: str) -> None:
    """This function writes a string to a file
    Args:
      script: The string to write to file
      filenameWithPath: A string containing a path and filename capable
                        of being 'written' by the executor of this script
    Returns:
      None
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
    
    try:
      fp.close()
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error closing file: {e}')
      raise

    if self.debug:
      print('Wrote custom bidding script to tmp file')

  def read_last_upload_file(self,
                            filename_with_path: str) -> str:
    """This function reads the last uploaded file and
    returns it as a string.  If the file cannot be found
    then an empty string is returned.
    Args:
      filename_with_path - a string containing a full path to a file.
    Returns:
      The contents of the file or an empty string if the file cannot be found.
    """
    # Set the default return value of empty string.
    data = ""

    # Try to open the file.
    try:
      fp = open(filename_with_path,'r')
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

    try:
      fp.close()
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error closing file: {e}')
      raise

    return data

  def write_last_upload_file(self,
                             filename_with_path: str,
                             script: str) -> bool:
    """This function writes the last uploaded file.
    Args:
      filename_with_path - full path to file to write script to.
      script - the script to write to file as a string
    Returns:
      True on success, False otherwise
    """
    # Try to open the file for write.
    try:
      fp = open(filename_with_path,'w')
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error opening last update ',
            f'file {filename_with_path} for write: {e}')
      return False
    
    try:
      fp.write(script)
    except (IOError, OSError) as e:
      print(f'Error writing local file: {e}')
      return False

    try:
      fp.close()
    except (FileNotFoundError, PermissionError, OSError) as e:
      print(f'Error closing file: {e}')
      raise

    return True


  def print_data_frame(self,
                       input_df: DataFrame) -> None:
    """Converts a dataframe to a string and prints it to stdout
    Args:
      input_df: any dataframe
    Returns:
      None
    """
    if self.debug:
      print(input_df.to_string())


  def generate_cb_script_max_of_conversion_counts (self,
                                                   zone_string: str,
                                                   test_run:bool=False) -> str:
    """Generate a Custom Bidding script based on Max conversion counts across
      a single sales zone.
    Args:
      zone_string: the name of the sales zone.  The associated Google Sheets
        workbook is expected to have a tab with the same name as this string
      test_run: Boolean indicating whether this custom bidding script generation
        call is a test run.  Test run output is sent to a different cell on the
        'CB_Scripts' tab in the associated Google Sheet.
    Returns:
      A fully formed custom bidding script suitable for upload to DV360
    """
    if self.debug:
      print('In generate_cb_script_max_of_conversion_counts() - sheet:',
            self.sheet.sheet_id)
      print('In generate_cb_script_max_of_conversion_counts() - zone_string:',
            zone_string)

    try:
      ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(
        zone_string)
      list_of_dicts = ref.get_all_records()      
    except gspread.exceptions.SpreadsheetNotFound:
      print("Error: Spreadsheet not found while.")
    except gspread.exceptions.WorksheetNotFound:
        print("Error: Worksheet not found.")
    except gspread.exceptions.APIError as e:
        print(f"Error connecting to worksheet for get_all_records(): {e}")
    except gspread.exceptions.GSpreadException as e:
        print(f"An unexpected error occurred: {e}")
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(
          zone_string)
      # For all other errors raise the exception
      else:
        print(f'Error with Sheets trying to open Sheet:{e}')
        raise
    except (ValueError, TypeError) as e:
        print(f"Error reading values from get_all_records(): {e}")
    except TimeoutError:
      print("""Request timed out while opening spreadsheet.
            Please check your network connection.""")
      raise  # Reraise the exception

    if self.debug:
      print(f"list_of_dicts[] active items returned from Sheets:")
      for item in list_of_dicts:
        if item['Generate Custom Bidding'].lower() == 'yes':
          print(f"ID :{item['Line Item ID']}, ",
                f"Bidding Factor:{item['Bidding Factor']}")

    if not self.alternate_algorithm:
      cust_bidding_function_string = 'return max_aggregate(['
    else:
      cust_bidding_function_string = ''

    conditional_prefix = ''

    processed_line_items = []
    for row in list_of_dicts:
      if row['Generate Custom Bidding'].lower() == 'yes':
        factor = row['Bidding Factor']
        line_item_id = row['Line Item ID']

        # Calculate a 'sane' bidding factor value within the
        # bounds of high/low settings.
        verified_factor = min(
          max(factor,self.bidding_factor_low),
          self.bidding_factor_high)

        # Conduct checks on the retrieved values of factor and line_item_id
        # to ensure they are valid numbers.  The lineItemID must be an
        # integer and the factor should be a float in a sensible range
        # low >= BIDDING_FACTOR_LO (default 0.5) and
        # high <= BIDDING_FACTOR_HIGH (default 1000).

        if self.is_number(factor) and line_item_id:

          # If the line item ID does not exist in our list of processed
          # line item IDs then add to the custom bidding function string
          # and add this ID to the list of processed items.
          if processed_line_items.count(row["Line Item ID"]) == 0:

            if not self.alternate_algorithm:
              # Loop and create a separate line for each floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                cust_bidding_function_string += \
                  f"\n  ([total_conversion_count(" + \
                  f"{floodlight_id_item},{self.attr_model_id})>0, "
                cust_bidding_function_string += \
                  f"line_item_id == {line_item_id}], "
                cust_bidding_function_string += \
                  f'{verified_factor}),'
            else:
              # Loop and create a separate if construct for each
              # floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                if len(processed_line_items) == 0:
                  conditional_prefix = ''
                else:
                  conditional_prefix = 'el'

                cust_bidding_function_string += \
                  f'\n{conditional_prefix}if line_item_id == {line_item_id}:'
                cust_bidding_function_string += \
                  f'\n  return total_conversion_count'
                cust_bidding_function_string += \
                  f'({floodlight_id_item},{self.attr_model_id}) * '
                cust_bidding_function_string += \
                  f'{verified_factor}'

            # We have processed this line item id, add it to the
            # list of processed items.
            processed_line_items.append(row['Line Item ID'])

    # Remove trailing comma as we're out of the for loop now so
    # no further lines.
    if not self.alternate_algorithm:
      for floodlight_id_item in self.floodlight_id_list:
        cust_bidding_function_string += \
          "\n  ([total_conversion_count(" + \
          f"{floodlight_id_item},{self.attr_model_id})>0], "
        cust_bidding_function_string += \
          f"{min(max(0.5,self.bidding_factor_low),self.bidding_factor_high)}),"
      # Remove final comma & insert close right square bracket and
      # close parenthasis to finalize array and function.
      cust_bidding_function_string = cust_bidding_function_string.rstrip(',')
      cust_bidding_function_string += "])"
    else:
      cust_bidding_function_string += '\nelse:\n  return 0'

    if self.debug:
      print(f'length of processedLineItems: {len(processed_line_items)}')

    if len(processed_line_items) == 0:
      cust_bidding_function_string = 'return 0;'

    # Update the tab named 'CB_Scripts' in the associated spreadsheet.
    # Spreadsheet tab name should match key in dict.
    update_row = None
    try:
      cbscripts_sheet = \
        self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet("CB_Scripts")
    except gspread.exceptions.SpreadsheetNotFound:
      print("Error: Spreadsheet not found for worksheet CB_Scripts.")
      raise # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound as e:
      print(f'Error connecting to worksheet CB_Scripts: {e}')
      raise # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print('Error communicating with Google Sheets API for ',
            f'worksheet CB_Scripts: {e}')
      raise # Reraises the exception.
    except TimeoutError:
      print("Request timed out. Please check your network connection.")
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f"An unexpected error occurred: {e}")
      raise # Reraises the exception.
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        cbscripts_sheet = \
          self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet("CB_Scripts")
      # For all other errors raise the exception
      else:
        print(f'Error with Sheets trying to open Sheet:{e}')
        raise

    # Direct mapping from zone_string to row location
    # in CB_Scripts tab in Sheets.
    if zone_string.lower() == "az":
      update_row = 2
    elif zone_string.lower() == "cz":
      update_row = 3
    elif zone_string.lower() == "ez_en":
      update_row = 4
    elif zone_string.lower() == "ez_fr":
      update_row = 5
    elif zone_string.lower() == "wz":
      update_row = 6
    else:
      print(f'Issue: passed zone_string "{zone_string}" ',
            'does not match expected inputs')

    # Write the most recent custom bidding function to the right
    # place on the CB_Scripts tab.
    if update_row:
      if test_run:
        try:
          cbscripts_sheet.update(
            values=[[cust_bidding_function_string,f"{datetime.now()}"]],
            range_name=f'D{update_row}')
        except gspread.exceptions.SpreadsheetNotFound:
          print("Error: writing to CB_Scripts tab.")
          raise # Reraises the exception.
        except gspread.exceptions.WorksheetNotFound as e:
          print(f'Error connecting to worksheet CB_Scripts: {e}')
          raise # Reraises the exception.
        except gspread.exceptions.APIError as e:
          print('Error communicating with Google Sheets API for ',
                f'worksheet CB_Scripts: {e}')
          raise # Reraises the exception.
        except TimeoutError:
          print("Request timed out. Please check your network connection.")
          raise # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(f"An unexpected error occurred: {e}")
          raise # Reraises the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
            cbscripts_sheet.update(
              values=[[cust_bidding_function_string,f"{datetime.now()}"]],
              range_name=f'D{update_row}')
          # For all other errors raise the exception
          else:
            print(f'Error with writing to CB_Scripts tab:{e}')
            raise

      else:
        try:
          cbscripts_sheet.update(
            values=[[cust_bidding_function_string,f"{datetime.now()}"]],
            range_name=f'B{update_row}')
        except gspread.exceptions.SpreadsheetNotFound:
          print("Error: updating CB_Scripts tab.")
          raise # Reraises the exception.
        except gspread.exceptions.WorksheetNotFound as e:
          print(f'Error connecting to worksheet CB_Scripts: {e}')
          raise # Reraises the exception.
        except gspread.exceptions.APIError as e:
          print('Error communicating with Google Sheets API for ',
                f'worksheet CB_Scripts: {e}')
          raise # Reraises the exception.
        except TimeoutError:
          print("Request timed out. Please check your network connection.")
          raise # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(f"An unexpected error occurred: {e}")
          raise # Reraises the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
            cbscripts_sheet.update(
              values=[[cust_bidding_function_string,f"{datetime.now()}"]],
              range_name=f'B{update_row}')

          # For all other errors raise the exception
          else:
            print(f'Error updating CB_Scripts tab:{e}')
            raise

    return cust_bidding_function_string