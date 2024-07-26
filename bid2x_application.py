import httplib2
import gspread

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from bid2x_spreadsheet import bid2x_spreadsheet
from datetime import datetime
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError

class bid2x_application():

  trix = None
  scopes = None

  dv_service = None
  dv_api_name = None
  dv_api_version = None

  sheet = None
  zone_array = None

  # TODO: b/359901129 - Create data class for attributes bid2x_application.
  action_list_algos = False
  action_list_scripts = False
  action_create_algorithm = False
  action_update_spreadsheet = False
  action_remove_algorithm = False
  action_update_scripts = False
  action_test = False

  debug = False
  clear_onoff = True             # Clean up custom bidding flag in sheet.
  defer_pattern = False          # Update script creation flag in sheets.
  alternate_algorithm = False    # Alt algo flag for each floodlight.

  new_algo_name = 'bid2inventory'             # Custom Bidding algo name.
  new_algo_display_name = 'bid2inventory'     # Custom Bidding algo display name.
  line_item_name_pattern = 'bid-to-invenotry' # Pattern in LI to pickup for algo.

  json_auth_file = None
  cb_tmp_file_prefix = '/tmp/cb_script'       # Temp locatiom for CB script.
  cb_last_update_file_prefix = 'last_upload'  # Prefix for last updated script.

  partner_id = 0             # Partner ID for the custom bidding script.
  advertiser_id = 0          # Advertiser ID for the custom bidding script.
  cb_algo_id = 0             # Algo ID of the custom bidding script.
  service_account_email = 'bid2x@test.com'  # Cloud Service Account E-mail.

  zones_to_process = 'CZ'       # Zones involved in the bidding script.
  floodlight_id_list = None     # List of Floodlight IDs involved in script.
  attr_model_id = 0             # Attribution Model ID for Floodlights.
  bidding_factor_high = 1000.0  # Max bidding factor.
  bidding_factor_low = 0.5      # Min bidding factor.

  def __init__(self, trix, scopes, dv_api_name, dv_api_version, sheet_id, auth_file):
    self.trix = trix
    self.scopes = scopes
    self.dv_api_name = dv_api_name
    self.dv_api_version = dv_api_version
    self.dv_service = None
    self.sheet = bid2x_spreadsheet(sheet_id,auth_file)
    self.zone_array = []

  def __str__(self):
    print(f'trix: {self.trix}')
    print(f'dv_api_name: {self.dv_api_name}')
    print(f'dv_api_version: {self.dv_api_version}')

  def setTrix(self,str_trix):
    self.trix = str_trix

  def setScopes (self,str_scopes):
    self.scopes = str_scopes

  def auth_dv(self, auth_file, auth_email_account):
    """Top level function for auth'ing to DV360

    Args:
      auth_file: An authentication file in json format
      auth_email_account: The email account (typically a service account) under
        which the auth file is to be used

    Returns:
      Returns True if able to create a good .dv_service object within this class,
      Otherwise it returns False.
    """
    dv_http_service = self.auth_dv_service(auth_file, auth_email_account)

    # Build a service object for interacting with the API.
    if dv_http_service:
        self.dv_service = discovery.build(self.dv_api_name,
                                          self.dv_api_version, http=dv_http_service)
    else:
        print(f"Error authenticating using provided JSON information")
        return False

    return self.dv_service


  def auth_dv_service(self,path_to_service_account_json_file,impersonation_email):
    """Creates credentials based on a service account and email

    Args:
      path_to_service_account_json_file: file downloaded from GCP
      impersonation_email: service account email address

    Returns:
      Returns http object
    """

    """Authorizes an httplib2.Http instance using service account credentials."""
    # Load the service account credentials from the specified JSON keyfile.
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        path_to_service_account_json_file,
        scopes=self.scopes)

    # Configure impersonation (if applicable).
    if impersonation_email:
        credentials = credentials.create_delegated(impersonation_email)

    # Use the credentials to authorize an httplib2.Http instance.
    dv_http_service = credentials.authorize(httplib2.Http())

    if dv_http_service:
      self.dv_service = discovery.build(self.dv_api_name, self.dv_api_version, http=dv_http_service)

    return dv_http_service


  def auth_sheets(self, auth_file, auth_email_account):
    # Set up service object to talk to Google Sheets.
    sheets_service = self.auth_sheets_service(auth_file, auth_email_account)

    # Build a service object for interacting with the API.
    if not sheets_service:
        print(f"Error authenticating sheets using provided JSON information")
        return False
    else:
       self.sheet.sheets_service = sheets_service

    return sheets_service


  def auth_sheets_service(self, path_to_service_account_json_file,impersonation_email):
    """Authorizes an httplib2.Http instance using service account credentials."""
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


  def listPartnerAlgoScripts(self, service,partner_id,algorithm_id):
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

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while listing partner scripts:{e}')

    return response


  def listAdvertiserAlgoScripts(self, service,advertiser_id,algorithm_id):
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

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while listing advertiser scripts:{e}')

    return response


  def listAdvertiserAlgorithms(self, service, advertiser_id):
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
    request = service.customBiddingAlgorithms().list(advertiserId=advertiser_id)

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while listing advertiser algorithms:{e}')

    return response


  def listPartnerAlgorithms(self, service, partner_id):
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

    request = service.customBiddingAlgorithms().list(partnerId=partner_id)

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while listing partner algorithms:{e}')

    return response


  def createCBAlgorithmPartner(self, service, advertiser_id, partner_id, cb_script_name, cb_display_name):
    """This function creates a partner-level custom bidding algorithm.

    Args:
      service: an active service connection object to DV360
      advertiserId: the advertiser ID to create the custom
                    bidding algo for
      partnerId: the partnerId to create the custom bidding algorithm under

    Returns:
      The DV360 response from creating the new custom bidding algorithm in JSON format
    """

    custom_bidding_model_details = {
      "advertiserId": f'{advertiser_id}',
      "readinessState": 'READINESS_STATE_TRAINING',
      "suspensionState": 'SUSPENSION_STATE_UNSPECIFIED' }

    custom_bidding_algorithm = {
      "name": cb_script_name,
      "displayName": cb_display_name,
      "entityStatus": 'ENTITY_STATUS_ACTIVE',
      "customBiddingAlgorithmType": 'SCRIPT_BASED',
      "sharedAdvertiserIds": [
        advertiser_id
      ],
      "modelDetails": [
          custom_bidding_model_details
      ],
      "partnerId": f'{partner_id}'
    }

    request = service.customBiddingAlgorithms().create(body=custom_bidding_algorithm)
    response = request.execute()

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while creating partner-level c.b. algorithm:{e}')

    return response


  def createCBAlgorithmAdvertiser(self, service, advertiser_id, cb_script_name, cb_display_name):
    """This function creates an advertiser-level custom bidding algorithm.

    Args:
      service: an active service connection object to DV360
      advertiserId: the advertiser ID to create the custom
                    bidding algo for

    Returns:
      The DV360 response from creating the new custom bidding algorithm in JSON format
    """

    custom_bidding_model_details = {
      "advertiserId": f'{advertiser_id}',
      "readinessState": 'READINESS_STATE_TRAINING',
      "suspensionState": 'SUSPENSION_STATE_UNSPECIFIED' }

    custom_bidding_algorithm = {
      "name": cb_script_name,
      "displayName": cb_display_name,
      "entityStatus": 'ENTITY_STATUS_ACTIVE',
      "customBiddingAlgorithmType": 'SCRIPT_BASED',
      "sharedAdvertiserIds": [
        advertiser_id
      ],
      "modelDetails": [
          custom_bidding_model_details
      ],
      "advertiserId": f'{advertiser_id}'
    }

    print(f'built request = {custom_bidding_algorithm}')
    # quit()

    request = service.customBiddingAlgorithms().create(body=custom_bidding_algorithm)
    response = request.execute()

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while creating advertiser-level c.b. algorithm:{e}')

    return response


  def removeCBAlgorithmPartner(self, service, partner_id, algorithm_id):
    """This function removes a partner-level custom bidding algorithm

    Args:
      service: an active service connection object to DV360
      partnerId: the partner ID of the partner under which the C.B. algo
                to remove currently lives

    Returns:
      The DV360 response from deleting the custom bidding algorithm in JSON format
    """

    entity_status = {
      'partnerId':f'{partner_id}',
      'entityStatus':'ENTITY_STATUS_ARCHIVED'
    }

    request = service.customBiddingAlgorithms().patch(
      customBiddingAlgorithmId=f'{algorithm_id}',
      updateMask="entityStatus",
      body=entity_status)

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while removing partner-level algorithm:{e}')

    return response

  def removeCBAlgorithmAdvertiser(self, service, advertiser_id, algorithm_id):
    """This function removes an advertiser-level custom bidding algorithm

    Args:
      service: an active service connection object to DV360
      advertiserId: the ID of the advertiser under which the C.B. algo
                to remove currently lives

    Returns:
      The DV360 response from deleting the custom bidding algorithm in JSON format
    """

    entity_status = {
      'advertiserId':f'{advertiser_id}',
      'entityStatus':'ENTITY_STATUS_ARCHIVED'
    }

    request = service.customBiddingAlgorithms().patch(
      customBiddingAlgorithmId=f'{algorithm_id}',
      updateMask="entityStatus",
      body=entity_status)

    try:
      response = request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400, 401, 403, 404, 500)
      print(f'An HTTP error occurred: {e}')
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Error with DV360 while removing advertiser-level algorithm:{e}')

    return response


  def writeTmpFile(self, script, filename_with_path):
    """This function writes a string to a file

    Args:
      script: The string to write to file
      filenameWithPath: A string containing a path and filename capable
                        of being 'written' by the executor of this script

    """

    # Write file to tmp location.
    try:
      fp = open(filename_with_path,'w')
      fp.write(script)
      fp.close()
    except OSError as e:
      print(f'Error writing local file: {e}')

    if self.debug:
      print('Wrote cb script to tmp file')


  def readLastUploadFile(self, filename):
    """This function reads the last uploaded file and
    returns it as a string.  If the file cannot be found
    then an empty string is returned.

    Args:
      None
    Returns:
      The contents of the last uploaded file or an empty
      string if the file cannot be found.
    """
    # Set the default return value.
    data = ""

    # Try to open the file.
    try:
      fp = open(filename,'r')
    except OSError as e:
      print(f'Error opening last update file: {e}')

      # clear error
      pass
      fp = None

    if fp:
      data = fp.read()
      fp.close()

    return data


  def writeLastUploadFile(self, filename, script):
    """This function writes the last uploaded file.

    Args:
      script - the script to write to file
    Returns:
      0 on success, anything else otherwise

    """

    # Try to open the file for write.
    try:
      fp = open(filename,'w')
    except OSError as e:
      print(f'Error opening last update file {filename} for write: {e}')
      return False

    try:
      fp.write(script)
      fp.close()
    except OSError as e:
      print(f'Error writing to last update file: {e}')
      return False

    return 0


  def printDataFrame(self,input_df):
    """Converts a dataframe to a string and prints it to stdout
    Args:
      input_df: any dataframe

    Returns:
      None
    """
    if self.debug:
      print(input_df.to_string())


  def is_number(self, s):
    """is the passed variable a number?
    Args:
      s: any variable

    Returns:
      True if the passed variable evaluates to a number or a string containing a number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


  def generate_cb_script_max_of_conversion_counts (self, zone_string, test_run=False):
    """Generate a Custom Bidding script based on Max conversion counts across
      a single sales zone.
    Args:
      zone_string: the name of the sales zone.  The associated Google Sheets workbook
        is expected to have a tab with the same name as this string
      test_run: Boolean indicating whether this custom bidding script generation
        call is a test run.  Test run output is sent to a different cell on the
        'CB_Scripts' tab in the associated Google Sheet.

    Returns:
      A fully formed custom bidding script suitable for upload to DV360
    """
    # Connect to Sheets to get list of line items.
    # gc = gspread.service_account(filename=self.json_auth_file)

    try:
      ref = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet(zone_string)
      list_of_dicts = ref.get_all_records()
    except gspread.exceptions.SpreadsheetNotFound:
      print("Error: Spreadsheet not found while.")
    except gspread.exceptions.WorksheetNotFound:
        print("Error: Worksheet not found.")
    except gspread.exceptions.APIError as e:
        print(f"Error connecting to worksheet for get_all_records(): {e}")
    except TimeoutError:
        print("Request timed out. Please check your network connection.")
    except (ValueError, TypeError) as e:
        print(f"Error reading values from get_all_records(): {e}")
    except gspread.exceptions.GSpreadException as e:
        print(f"An unexpected error occurred: {e}")

    if self.debug:
      print(f"list_of_dicts[] active items returned from Sheets:")
      for item in list_of_dicts:
        if item['Generate Custom Bidding'].lower() == 'yes':
          print(f"ID :{item['Line Item ID']}, Bidding Factor:{item['Bidding Factor']}")
      print("\n")

    if not self.alternate_algorithm:
      cust_bidding_function_string = 'return max_aggregate(['
    else:
      cust_bidding_function_string = ''

    conditional_prefix = ''

    processed_line_items = [];
    for row in list_of_dicts:
      if row['Generate Custom Bidding'].lower() == 'yes':
        factor = row['Bidding Factor']
        line_item_id = row['Line Item ID']

        # Conduct checks on the retrieved values of factor and line_item_id
        # to ensure they are valid numbers.  The lineItemID must be an
        # integer and the factor should be a float in a sensible range
        # low >= BIDDING_FACTOR_LO (default 0.5) and high <= BIDDING_FACTOR_HIGH
        # (default 1000).

        if self.is_number(factor) and line_item_id:

          # If the line item ID does not exist in our list of processed
          # line item IDs then add to the custom bidding function string
          # and add this ID to the list of processed items.
          if processed_line_items.count(row["Line Item ID"]) == 0:

            if not self.alternate_algorithm:
              # Loop and create a separate line for each floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                cust_bidding_function_string += f"\n  ([total_conversion_count({floodlight_id_item},{self.attr_model_id})>0, "
                cust_bidding_function_string += f"line_item_id == {line_item_id}], "
                cust_bidding_function_string += f"{min(max(factor,self.bidding_factor_low),self.bidding_factor_high)}),"
            else:

              # Loop and create a separate if construct for each floodlight in the list.
              for floodlight_id_item in self.floodlight_id_list:
                if len(processed_line_items) == 0:
                  conditional_prefix = ''
                else:
                  conditional_prefix = 'el'

                cust_bidding_function_string += f'\n{conditional_prefix}if line_item_id == {line_item_id}:'
                cust_bidding_function_string += f'\n  return total_conversion_count'
                cust_bidding_function_string += f'({floodlight_id_item},{self.attr_model_id}) * '
                cust_bidding_function_string += f'{min(max(factor,self.bidding_factor_low),self.bidding_factor_high)}'

            # We have processed this line item id, add it to the list of processed items.
            processed_line_items.append(row['Line Item ID'])

    # Remove trailing comma as we're out of the for loop now so
    # no further lines.
    if not self.alternate_algorithm:

      cust_bidding_function_string += f"\n  ([total_conversion_count({floodlight_id_item},{self.attr_model_id})>0], "
      cust_bidding_function_string += f"{min(max(0.5,self.bidding_factor_low),self.bidding_factor_high)})"

      # Insert close right square bracket and close parenthasis to
      # finalize array and function.
      cust_bidding_function_string += "])"
    else:
      cust_bidding_function_string += '\nelse:\n  return 0'

    if self.debug:
      print(f'length of processedLineItems: {len(processed_line_items)}')

    if len(processed_line_items) == 0:
      cust_bidding_function_string = 'return 0;'

    # Update CB_Scripts tab
    # Spreadsheet tab name should match key in dict.
    update_row = None
    try:
      cbscripts_sheet = self.sheet.gc.open_by_key(self.sheet.sheet_id).worksheet("CB_Scripts")
    except gspread.exceptions.SpreadsheetNotFound:
      print("Error: Spreadsheet not found for worksheet CB_Scripts.")
      raise # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound as e:
      print(f'Error connecting to worksheet CB_Scripts: {e}')
      raise # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print(f"Error communicating with Google Sheets API for worksheet CB_Scripts: {e}")
      raise # Reraises the exception.
    except TimeoutError:
      print("Request timed out. Please check your network connection.")
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f"An unexpected error occurred: {e}")
      raise # Reraises the exception.

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
      print(f'Issue: passed zone_string "{zone_string}" does not match expected inputs')

    # Write the most recent custom bidding function to the right place on the CB_Scripts tab.
    if update_row:
      if test_run:
        try:
          cbscripts_sheet.update(values=[[cust_bidding_function_string,f"{datetime.now()}"]], range_name=f'D{update_row}')
        except gspread.exceptions.APIError as e:
          print(f"Error communicating with Google Sheets API while updating test run into worksheet: {e}")
          raise # Reraises the exception.
        except TimeoutError:
          print("Request timed out. Please check your network connection.")
          raise # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(f"An unexpected error occurred updating test run into worksheet: {e}")
          raise # Reraises the exception.
      else:
        try:
          cbscripts_sheet.update(values=[[cust_bidding_function_string,f"{datetime.now()}"]], range_name=f'B{update_row}')
        except gspread.exceptions.APIError as e:
          print(f"Error communicating with Google Sheets API while updating test run into worksheet: {e}")
          raise # Reraises the exception.
        except TimeoutError:
          print("Request timed out. Please check your network connection.")
          raise # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(f"An unexpected error occurred: {e}")
          raise # Reraises the exception.

    return cust_bidding_function_string
