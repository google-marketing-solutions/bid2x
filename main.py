"""
  BidToInventory for DV360

  2024 - Google Inc

  DV360 partnerID:

  This Python application can be used to create a DV360 Custom Bidding Scipt based...


  This application can also be used to list custom bidding algorithms, create new algorithms,
  delete custom bidding algorithms, and list custom bidding scripts through the use of the
  -a<X> arguments.

  Overriding the default partner ID, advertiser ID, algorithm ID, debug level, index file,
  JSON authentication file, service account, and tmp file location are also all available
  through various arguments.

  Consult the accompanying 'requirements.txt' file for the list of dependancies.

  NOTE: GLOBAL VARIABLES SET HERE.  PLEASE ENSURE THE ENVIRONMENT IS CLEAN OR THERE
        ARE NO CONFLICTING VARIABLE NAMES.
"""

# Import required libraries & modules
import json
import os
import base64
import functions_framework
import sys

from distutils.util import strtobool
from datetime import datetime
from dotenv import load_dotenv
from bid2x_model import bid2x_model
from bid2x_application import bid2x_application
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from googleapiclient.discovery import build

# TODO: b/360122832 - Change environment variables input back to command-line arguments.
def process_environment_vars():
  global ACTION_LIST_ALGOS
  global ACTION_LIST_SCRIPTS
  global ACTION_CREATE_ALGORITHM
  global ACTION_UPDATE_SPREADSHEET
  global ACTION_REMOVE_ALGORITHM
  global ACTION_UPDATE_SCRIPTS
  global ACTION_TEST
  global DEBUG
  global CLEAR_ONOFF
  global DEFER_PATTERN
  global ALTERNATE_ALGORITHM

  global NEW_ALGO_NAME
  global NEW_ALGO_DISPLAY_NAME
  global LINE_ITEM_NAME_PATTERN
  global JSON_AUTH_FILE
  global CB_TMP_FILE_PREFIX
  global CB_LAST_UPDATE_FILE_PREFIX
  global PARTNER_ID
  global ADVERTISER_ID
  global CB_ALGO_ID
  global SERVICE_ACCOUNT_EMAIL
  global ZONES_TO_PROCESS
  global FLOODLIGHT_ID_LIST
  global ATTR_MODEL_ID
  global BIDDING_FACTOR_HIGH
  global BIDDING_FACTOR_LOW
  global SPREADSHEET_URL
  global SPREADSHEET_KEY
  global COLUMN_STATUS
  global COLUMN_LINEITEMID
  global COLUMN_LINEITEMNAME
  global COLUMN_LINEITEMTYPE
  global COLUMN_CAMPAIGNID
  global COLUMN_ADVERTISERID
  global COLUMN_CUSTOMBIDDING

  # Extract run-time parameters from environment variables setting a default
  # when the parameter doesn't exist.
  ACTION_LIST_ALGOS = strtobool(os.getenv('ACTION_LIST_ALGOS','false'))
  ACTION_LIST_SCRIPTS = strtobool(os.getenv('ACTION_LIST_SCRIPTS','false'))
  ACTION_CREATE_ALGORITHM = strtobool(os.getenv('ACTION_CREATE_ALGORITHM','false'))
  ACTION_UPDATE_SPREADSHEET = strtobool(os.getenv('ACTION_UPDATE_SPREADSHEET','false'))
  ACTION_REMOVE_ALGORITHM = strtobool(os.getenv('ACTION_REMOVE_ALGORITHM','false'))
  ACTION_UPDATE_SCRIPTS = strtobool(os.getenv('ACTION_UPDATE_SCRIPTS','false'))
  ACTION_TEST = strtobool(os.getenv('ACTION_TEST','false'))
  DEBUG = strtobool(os.getenv('DEBUG','false'))
  CLEAR_ONOFF = strtobool(os.getenv('CLEAR_ONOFF','true'))
  DEFER_PATTERN = strtobool(os.getenv('DEFER_PATTERN','true'))
  ALTERNATE_ALGORITHM = strtobool(os.getenv('ALTERNATE_ALGORITHM','false'))

  NEW_ALGO_NAME = os.getenv('NEW_ALGO_NAME','bid2Inventory')
  NEW_ALGO_DISPLAY_NAME = os.getenv('NEW_ALGO_DISPLAY_NAME','bid2Inventory')
  LINE_ITEM_NAME_PATTERN = os.getenv('LINE_ITEM_NAME_PATTERN',"bid-to-inventory")
  JSON_AUTH_FILE = os.getenv('JSON_AUTH_FILE','<CLIENT>-apps.json')
  CB_TMP_FILE_PREFIX = os.getenv('CB_TMP_FILE_PREFIX','/tmp/cb_script')
  CB_LAST_UPDATE_FILE_PREFIX = os.getenv('CB_LAST_UPDATE_FILE_PREFIX','last_upload')
  PARTNER_ID = int(os.getenv('PARTNER_ID',<CLIENT_PARTNER_ID>))
  ADVERTISER_ID = int(os.getenv('ADVERTISER_ID',<CLIENT_ADVERTISER_ID>))
  CB_ALGO_ID = int(os.getenv('CB_ALGO_ID',<CLIENT_ALGO_ID>))
  SERVICE_ACCOUNT_EMAIL = os.getenv('SERVICE_ACCOUNT_EMAIL','gmp-bid-to-inventory@<CLIENT>-apps.iam.gserviceaccount.com')
  ZONES_TO_PROCESS = os.getenv('ZONES_TO_PROCESS','cz,ez_en')
  FLOODLIGHT_ID_LIST = os.getenv('FLOODLIGHT_ID_LIST',[<CLIENT_FLOODLIGHT_IDS>])
  ATTR_MODEL_ID = int(os.getenv('ATTR_MODEL_ID',0))
  BIDDING_FACTOR_HIGH = float(os.getenv('BIDDING_FACTOR_HIGH',1000))
  BIDDING_FACTOR_LOW = float(os.getenv('BIDDING_FACTOR_LOW',0.5))
  SPREADSHEET_URL = os.getenv('SPREADSHEET_URL',
                              'https://docs.google.com/spreadsheets/d/<CLIENT_SHEETS>/edit')
  SPREADSHEET_KEY = os.getenv('SPREADSHEET_KEY','<CLIENT_SHEETS_KEY>')
  COLUMN_STATUS = os.getenv('COLUMN_STATUS','A')
  COLUMN_LINEITEMID = os.getenv('COLUMN_LINEITEMID','B')
  COLUMN_LINEITEMNAME = os.getenv('COLUMN_LINEITEMNAME','C')
  COLUMN_LINEITEMTYPE = os.getenv('COLUMN_LINEITEMTYPE','D')
  COLUMN_CAMPAIGNID = os.getenv('COLUMN_CAMPAIGNID','E')
  COLUMN_ADVERTISERID = os.getenv('COLUMN_ADVERTISERID','F')
  COLUMN_CUSTOMBIDDING = os.getenv('COLUMN_CUSTOMBIDDING','K')

# The default action in lieu of an usable environment is to perform
# an update to the Google sheet by using the *-update-sheet.env
# environment file.
load_dotenv('./<CLIENT>-update-sheet.env')
process_environment_vars()

API_SCOPES = [
  'https://www.googleapis.com/auth/display-video',
  'https://www.googleapis.com/auth/spreadsheets']
API_NAME = 'displayvideo'
API_VERSION = 'v2'

# Create an array of sales zones objects for client.
# Process the ZONES_TO_PROCESS string for a list of zones
# to include.
# The default is to add all sales zones based upon a default
# --zones option of "az,cz,ez_en,ez_fr,wz"
# A subset of zones can be processed by using the -z option e.g.
#   $ python main.py -ah -z AZ,CZ
# to process just the Atlantic and Central sales zones.

app = bid2x_application(
  SPREADSHEET_URL,
  API_SCOPES,
  API_NAME,
  API_VERSION,
  SPREADSHEET_KEY,
  JSON_AUTH_FILE)

app.zone_array = []

if ZONES_TO_PROCESS is None:
  ZONES_TO_PROCESS = 'cz,ez_en'
zone_list = ZONES_TO_PROCESS.split(",")
for zone in zone_list:
  if zone.lower() == 'az':
    #                                name,  campaign_id, advertiser_id,  algorithm_id, debug
    app.zone_array.append(bid2x_model("AZ",   <CLIENT_CAMPAIGN_ID_FOR_REGION_AZ>,   ADVERTISER_ID, <CLIENT_ADVERTISER_ID_FOR_AZ>, DEBUG))
  elif zone.lower() == 'cz':
    #                                name,  campaign_id, advertiser_id,  algorithm_id, debug
    app.zone_array.append(bid2x_model("CZ",   <CLIENT_CAMPAIGN_ID_FOR_REGION_CZ>,   ADVERTISER_ID, <CLIENT_ADVERTISER_ID_FOR_CZ>, DEBUG))
  elif zone.lower() == 'ez_en' or zone.lower() == 'ez-en':
    #                                name,  campaign_id, advertiser_id,  algorithm_id, debug
    app.zone_array.append(bid2x_model("EZ_EN",<CLIENT_CAMPAIGN_ID_FOR_REGION_EZ_EN>,   ADVERTISER_ID, <CLIENT_ADVERTISER_ID_FOR_EZ>, DEBUG))
  elif zone.lower() == 'ez_fr' or zone.lower() == 'ez-fr':
    #                                name,  campaign_id, advertiser_id,  algorithm_id, debug
    app.zone_array.append(bid2x_model("EZ_FR",<CLIENT_CAMPAIGN_ID_FOR_REGION_EZ_FR>,   ADVERTISER_ID, <CLIENT_ADVERTISER_ID_FOR_EZ_FR>, DEBUG))
  elif zone.lower() == 'wz':
    #                                name,  campaign_id, advertiser_id,  algorithm_id, debug
    app.zone_array.append(bid2x_model("WZ",   <CLIENT_CAMPAIGN_ID_FOR_REGION_WZ>,   ADVERTISER_ID, <CLIENT_ADVERTISER_ID_FOR_WZ>, DEBUG))


  app.trix = SPREADSHEET_URL
  app.scopes = API_SCOPES
  app.dv_api_name = API_NAME
  app.dv_api_version = API_VERSION

  app.action_list_algos = ACTION_LIST_ALGOS
  app.action_list_scripts = ACTION_LIST_SCRIPTS
  app.action_create_algorithm = ACTION_CREATE_ALGORITHM
  app.action_update_spreadsheet = ACTION_UPDATE_SPREADSHEET
  app.action_remove_algorithm = ACTION_REMOVE_ALGORITHM
  app.action_update_scripts = ACTION_UPDATE_SCRIPTS
  app.action_test = ACTION_TEST

  app.debug = DEBUG
  app.sheet.debug = DEBUG

  app.clear_onoff = CLEAR_ONOFF
  app.sheet.clear_onoff = CLEAR_ONOFF

  app.defer_pattern = DEFER_PATTERN
  app.alternate_algorithm = ALTERNATE_ALGORITHM

  app.new_algo_name = NEW_ALGO_NAME
  app.new_algo_display_name = NEW_ALGO_DISPLAY_NAME
  app.line_item_name_pattern = LINE_ITEM_NAME_PATTERN

  app.json_auth_file = JSON_AUTH_FILE
  app.cb_tmp_file_prefix = CB_TMP_FILE_PREFIX
  app.cb_last_update_file_prefix = CB_LAST_UPDATE_FILE_PREFIX

  app.partner_id = PARTNER_ID
  app.advertiser_id = ADVERTISER_ID
  app.cb_algo_id = CB_ALGO_ID
  app.service_account_email = SERVICE_ACCOUNT_EMAIL

  app.zones_to_process = ZONES_TO_PROCESS
  app.floodlight_id_list = FLOODLIGHT_ID_LIST
  app.attr_model_id = ATTR_MODEL_ID
  app.bidding_factor_high = BIDDING_FACTOR_HIGH
  app.bidding_factor_low = BIDDING_FACTOR_LOW


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    message = base64.b64decode(cloud_event.data["message"]["data"])
    print(f'Received pubsub message: {message}')

    if message == b'update_sheets':
      # Received pubsub message to update sheet - load environment
      load_dotenv('./<CLIENT>-update-sheet.env')
      process_environment_vars()
    elif message == b'update_cb':
      # Received pubsub message to upload new scripts
      load_dotenv('./<CLIENT>-upload.env')
      process_environment_vars()

    # now run main
    main(sys.argv)


def main(argv):

  print(f"DV360 Custom Bidding script - Startup  {datetime.now()}")

  try:
    SPREADSHEET_URL
  except NameError:
    print("No args exist, preload a known good set")
    # default action is to update the spreadsheet
    load_dotenv('./<CLIENT>-update-sheet.env')
    process_environment_vars()
  else:
    print("Args exist")
  if not app.auth_dv_service(app.json_auth_file, app.service_account_email):
    print(f'Failure on auth to DV')
    return False

  if not app.auth_sheets(app.json_auth_file, app.service_account_email):
    print(f'Failure on auth to Sheets')
    return False

  if not app.sheet.sheets_service:
    print(f"Error authenticating sheets using provided JSON information")
    return False

  if DEBUG:
    print("DV360 Custom Bidding update script - startup vars:")
    print("General settings:")
    print(f'  Debug is: {app.debug}')
    print(f'  DV service: {app.dv_service}')
    print(f'  DV service: {app.dv_service}')
    print(f'  Sheets service: {app.sheet.sheets_service}')
    print(f'  PARTNER_ID: {app.partner_id}')
    print(f'  ADVERTISER_ID: {app.advertiser_id}')
    print(f'  CB_ALGO_ID: {app.cb_algo_id}')
    print("Files:")
    print(f'  Service account email: {app.service_account_email}')
    print(f'  json file: {app.json_auth_file}')
    print(f'  tmp file prefix: {app.cb_tmp_file_prefix}')
    print(f'  last upload file prefix: {app.cb_last_update_file_prefix}')
    print("Actions:")
    print(f'  List scripts: {app.action_list_scripts}')
    print(f'  List algorithms: {app.action_list_algos}')
    print(f'  Create Algorithm: {app.action_create_algorithm}')
    print(f'  Remove Algorithm: {app.action_remove_algorithm}')
    print(f'  Update Script: {app.action_update_scripts}')
    print(f'  Update Spreadsheet: {app.action_update_spreadsheet}')
    print(f'  Test Action: {app.action_test}')

  # Is 'dv_service' (i.e. a conntection to DV360) valid?
  # If yes then proceed to process functions.
  if app.dv_service:

    if app.action_list_scripts:
      # Needs to be converted to multi-zone approach.
      # Show partner level scripts.
      print(f"Partner level scripts for algorithm ID = {CB_ALGO_ID}")
      response = app.listPartnerAlgoScripts(app.dv_service,app.partner_id,CB_ALGO_ID)
      json_pretty_print = json.dumps(response, indent=2)
      print(f"ret_val = {json_pretty_print}")

      # Show advertiser level scripts.
      print(f"Advertiser level scripts for algorithm ID = {CB_ALGO_ID}")
      response = app.listAdvertiserAlgoScripts(app.dv_service,app.advertiser_id,CB_ALGO_ID)
      json_pretty_print = json.dumps(response, indent=2)
      print(f"ret_val = {json_pretty_print}")

    if app.action_list_algos:
      # Show list of custom bidding algos from Advertiser level.
      print(f"Advertiser level algorithms")
      response = app.listAdvertiserAlgorithms(app.dv_service,app.advertiser_id)
      json_pretty_print = json.dumps(response, indent=2)
      print(f"ret_val = {json_pretty_print}")

      # Show list of custom bidding scripts from Partner level.
      print(f"Partner level algorithms")
      response = app.listPartnerAlgorithms(app.dv_service,app.partner_id)
      json_pretty_print = json.dumps(response, indent=2)
      print(f"ret_val = {json_pretty_print}")

    if app.action_create_algorithm:
      # Create a new custom bidding algorithm from Partner level.
      print("Attempt to create new custom bidding algorithm:")

      for zone in app.zone_array:
        # Create CB Algorithm at the Advertiser level.
        algorithmName = app.new_algo_name + "_" + zone.name
        displayName = app.new_algo_display_name + "_" + zone.name
        response = app.createCBAlgorithmAdvertiser(app.dv_service, app.advertiser_id, algorithmName, displayName)
        json_pretty_print = json.dumps(response, indent=2)
        if app.debug:
          print(f"new custom bidding algorithm response = {json_pretty_print}")

    if app.action_remove_algorithm:
      # Remove an advertiser custom bidding algorithm by ID.
      app.removeCBAlgorithmAdvertiser(app.dv_service, app.advertiser_id, app.cb_algo_id)

    if app.action_update_scripts:
      # Update the custom bidding scripts in DV360.

      # Create custom bidding script for DV360 as a string - per sales zone.
      for zone in app.zone_array:

        # Go into Google Sheets and generate CB function per sales zone.
        custom_bidding_function_string = app.generate_cb_script_max_of_conversion_counts(zone.name)

        # Get a list of line items this will affect.
        line_item_array = app.sheet.get_affected_line_items_from_sheet(zone.name,app.sheet.json_auth_file)

        if app.debug:
          # Show the generated custom bidding script.
          print(f'custom_bidding_function_string:\n{custom_bidding_function_string}\n')

        # Try to locate the last function that was uploaded to DV360 and compare
        # as we don't want to upload the exact same script due to a bud in DV360.
        last_update_filename = app.cb_last_update_file_prefix + '_' + zone.name + '.txt'
        custom_bidding_last_upload = app.readLastUploadFile(last_update_filename)

        # Write custom bidding script to a tmp file in local file system as
        # the upload mechanism to DV utilizes the local filesystem.
        tmp_file = app.cb_tmp_file_prefix + '_' + zone.name + '.txt'
        app.writeTmpFile(custom_bidding_function_string, tmp_file)

        if app.debug:
          print(f'new script :***{custom_bidding_function_string}***')
          print(f'last script:***{custom_bidding_last_upload}***')

        # Compare the new script and the previously uploaded script.
        if custom_bidding_function_string.strip() == custom_bidding_last_upload.strip():
          # The new script is the same as the old script, don't upload.
          print('New script is the same as the previously uploaded script; not uploading')
          return False
        else:
          print("New script is different from last uploaded script; uploading new version")

          # Make call to update script in DV360.
          if zone.updateCustomBiddingScripts(app.dv_service, zone.advertiser_id, zone.algorithm_id, tmp_file, line_item_array):
            # If update of CB script is successful then update LastUploadFile by
            # writing script to last upload file.
            if not app.writeLastUploadFile(last_update_filename,custom_bidding_function_string):
              print("Error writing last script upload to file")

    if app.action_test:
      for zone in app.zone_array:
        print(f"rules for zone {zone.name}:\n{app.generate_cb_script_max_of_conversion_counts(zone.name,test_run=True)}")

    if app.action_update_spreadsheet:
      if app.debug:
        print("app.dv_service",app.dv_service)
        print("app.line_item_name_pattern",app.line_item_name_pattern)
        print("app.zone_array",app.zone_array)
        print("app.defer_pattern",app.defer_pattern)
      app.sheet.read_dv_line_items (app.dv_service, app.line_item_name_pattern, app.zone_array, app.defer_pattern)

  else:
    print(f'Unable to connect to DV360; no service - stopped')
    return False

  print(f"DV360 Custom Bidding script - Finished {datetime.now()}")
  return True

if __name__ == '__main__':
  main(sys.argv)
