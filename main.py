"""
  BidToX for DV360

  Copyright 2024 Google Inc.

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

  This Python application can be used to dynamically create DV360 Custom
  Bidding Scipts.

  This application can also be used to list custom bidding algorithms,
  create new algorithms, delete custom bidding algorithms, and list custom
  bidding scripts through the use of the -a<X> arguments.

  Overriding the default partner ID, advertiser ID, algorithm ID, debug
  level, index file, JSON authentication file, service account, and tmp
  file location are also all available through various arguments.

  Consult the accompanying 'requirements.txt' file for the list of dependancies.
"""

# Import required libraries & modules
import json
import base64
import functions_framework
import sys

from datetime import datetime
from datetime import datetime
from dotenv import load_dotenv

from bid2x_model import bid2x_model
from bid2x_application import bid2x_application
from bid2x_env import process_environment_vars
from bid2x_args import process_command_line_args
import bid2x_var

# Triggered from a message on a Cloud Pub/Sub topic.
# For a deployment on Cloud Functions in GCP this function is the entry point.
@functions_framework.cloud_event
def hello_pubsub(cloud_event) -> None:
    # Print out the data from Pub/Sub, to prove that it worked
    message = base64.b64decode(cloud_event.data["message"]["data"])
    print(f'Received pubsub message: {message}')

    if message == b'update_sheets':
      # Received pubsub message to update sheet - load environment
      print("Received PubSub message to update_sheets - executing")
      # When executed through GCP Cloud Functions use environment var
      # files pre-loaded into GCP to set the context to run.  In this
      # case the update_sheets message forces the loading of the
      # update-sheet specific .env file.
      load_dotenv('./<client>-update-sheet.env')
      process_environment_vars()
    elif message == b'upload_cb':
      # Received pubsub message to upload new scripts
      print("Received PubSub message to upload new scripts - executing")
      # When executed through GCP Cloud Functions use environment var
      # files pre-loaded into GCP to set the context to run.  In this
      # case the upload_cb message forces the loading of the
      # upload specific .env file.
      load_dotenv('./<client>-upload.env')
      process_environment_vars()

    # Now that the environment variables have been used to set the scoped
    # vars, assign these to the app.* objects.
    bid2x_var.assign_vars_to_objects(app)

    # Now run the main loop.
    main(sys.argv)


def main(argv):

  print(f"DV360 Custom Bidding script - Startup  {datetime.now()}")

  try:
    bid2x_var.SPREADSHEET_URL
  except NameError:
    print("No args exist, preload a known good set")
    # default action is to update the spreadsheet
    load_dotenv('./<client>-update-sheet.env')
    process_environment_vars()

  if not app.auth_dv_service(app.json_auth_file, app.service_account_email):
    print(f'Failure on auth to DV')
    return False

  if not app.auth_sheets(app.json_auth_file, app.service_account_email):
    print(f'Failure on auth to Sheets')
    return False

  if not app.sheet.sheets_service:
    print(f"Error authenticating sheets using provided JSON information")
    return False

  # TODO: modify this to have the app object self-describe
  if bid2x_var.DEBUG:
    print("DV360 Custom Bidding update script - startup vars:")
    print("General settings:")
    print(f'  Debug is: {app.debug}')
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
      # Show advertiser level scripts for each initialized zone
      for zone in app.zone_array:
        print(f'Custom bidding scripts for zone {zone.name}',
              f' advertiser_id = {zone.advertiser_id}')
        response = app.list_advertiser_algo_scripts(app.dv_service,
                                                    zone.advertiser_id)
        json_pretty_print = json.dumps(response, indent=2)
        print(f"{json_pretty_print}")

    if app.action_list_algos:
      # Show advertiser level algorithms for each initialized zone
      print(f"Advertiser level algorithms for advertiser ID ",
            f"= {app.advertiser_id}")
      response = app.list_advertiser_algorithms(app.dv_service,
                                                app.advertiser_id)
      json_pretty_print = json.dumps(response, indent=2)
      print(f"{json_pretty_print}")

    if app.action_create_algorithm:
      # Create a new custom bidding algorithm from Partner level.
      print("Create new custom bidding algorithm for zone(s):")

      for zone in app.zone_array:
        # Create CB Algorithm at the Advertiser level.
        algorithmName = app.new_algo_name + "_" + zone.name
        displayName = app.new_algo_display_name + "_" + zone.name
        print(f'New algorithm name: {displayName}')
        response = app.create_cb_algorithm_advertiser(app.dv_service,
                                                      app.advertiser_id,
                                                      algorithmName,
                                                      displayName)
        if app.debug:
          json_pretty_print = json.dumps(response, indent=2)
          print(f"new custom bidding algorithm response = {json_pretty_print}")

    if app.action_remove_algorithm:
      # Remove an advertiser custom bidding algorithm by ID.
      print(f'Custom bidding algorithm id {app.cb_algo_id} will ',
            'attempted to be deleted.')
      response = app.remove_cb_algorithm_advertiser(app.dv_service,
                                                    app.advertiser_id,
                                                    app.cb_algo_id)

      print(f'result of deletion attempt: {response}')

    if app.action_update_scripts:
      # Update the custom bidding scripts in DV360.

      # Create custom bidding script for DV360 as a string - per sales zone.
      for zone in app.zone_array:
        # Go into Google Sheets and generate CB function per sales zone.
        custom_bidding_function_string = \
          app.generate_cb_script_max_of_conversion_counts(zone.name)
        
        if app.debug:
          # Show the generated custom bidding script.
          print('custom_bidding_function_string:\n',
                f'{custom_bidding_function_string}\n')
          
        # Get a list of line items this will affect.
        line_item_array = \
          app.sheet.get_affected_line_items_from_sheet(zone.name)
        # Get the current algorithm directly from DV360
        custom_bidding_current_script = \
          app.read_cb_algorithm_by_id(app.dv_service,
                                      app.advertiser_id,
                                      zone.algorithm_id)
        if app.debug:
          print(f'new c.b.script:***{custom_bidding_function_string}***')
          print(f'current script:***{custom_bidding_current_script}***')
        # Updating custom bidding scripts deals with Media objects - similar
        # to the handling of creatives.  These are typically files on a local
        # file system and it's easier to deal with the uploading of a custom
        # bidding script by placing it in a temp file.
        # Build the tmp filename using the custom budding (cb) tmp file prefix
        # an underscore and then the zone name along with a '.txt' suffix.
        # Once we check that the new CB script is actually new the contents
        # of the script will be written to this filename.
        filename = app.cb_tmp_file_prefix + "_" + zone.name + ".txt"
        # Compare the new script and the previously uploaded script.
        if str(custom_bidding_function_string).strip() == \
          str(custom_bidding_current_script).strip():
          # The new script is the same as the old script, don't write to file
          # and don't upload.  Just return False from this function.
          print('New script is the same as the existing script; not uploading')
          return False
        else:
          print("New script is different from last ",
                "uploaded script; uploading new version")
          # Write new script to tmp filename.  Upload is from a tmp file.
          app.write_last_upload_file(filename,custom_bidding_function_string)
          # Make call to update script in DV360 passing in filename containing
          # new script.
          update_result = zone.update_custom_bidding_scripts(
            app.dv_service,
            zone.advertiser_id,
            zone.algorithm_id,
            filename,
            line_item_array)

          if not update_result:
            print(f"Update of C.B. Script for zone {zone.name} failed.")
          else:
            print(f"Update of C.B. Script for zone {zone.name} succeeded.")
            # Update of C.B. script was successful, update the Google
            # Sheets spreadsheet tab named 'CB_Scripts'
            app.sheet.update_cb_scripts_tab(zone,
                                            custom_bidding_function_string,
                                            test_run=False)

    if app.action_test:
      # Generate the Custom Bidding Script.
      custom_bidding_string = app.generate_cb_script_max_of_conversion_counts(
        zone.name)
      # Print the value of the script to the console - since this runs 
      # typically as a Cloud Function then this will end up in the logs.
      print(f"""rules for zone {zone.name}:\n
            {custom_bidding_string}""")
      
      # Write the Test Run out to the test column in the associated
      # Google Sheet in the tab 'CB_Scripts'
      app.sheet.update_cb_scripts_tab(
        zone,
        custom_bidding_string,
        test_run=True)

    if app.action_update_spreadsheet:
      app.sheet.read_dv_line_items (app.dv_service,
                                    app.line_item_name_pattern,
                                    app.zone_array,
                                    app.defer_pattern)

  else:
    print(f'Unable to connect to DV360; no service - stopped')
    return False
  
  print(f"DV360 Custom Bidding script - Finished {datetime.now()}")
  return True

# Walk sys.argv using argparse to process passed arguments.
# The use of command line arguments is meant for development or for
# running the system from the command line.
process_command_line_args()

# Create an array of sales zones objects for Hyundai Canada.
# Process the ZONES_TO_PROCESS string for a list of zones
# to include.
# The default is to add all sales zones based upon a default
# --zones option of "az,cz,ez_en,ez_fr,wz"
# A subset of zones can be processed by using the -z option e.g.
#   $ python main.py -ah -z AZ,CZ
# to process just the Atlantic and Central sales zones.

# Need to load data here so that app & zones can be created
# with valid values.

app = bid2x_application(
  bid2x_var.SPREADSHEET_URL,
  bid2x_var.API_SCOPES,
  bid2x_var.API_NAME,
  bid2x_var.API_VERSION,
  bid2x_var.SPREADSHEET_KEY,
  bid2x_var.JSON_AUTH_FILE)

app.zone_array = []

if bid2x_var.ZONES_TO_PROCESS is None:
  bid2x_var.ZONES_TO_PROCESS = 'c1,c2'
zone_list = bid2x_var.ZONES_TO_PROCESS.split(",")
for zone in zone_list:
  if zone.lower() == 'c1':
    app.zone_array.append(
      bid2x_model("Campaign1",              # name
                  10000001,                 # campaign id
                  bid2x_var.ADVERTISER_ID,  # advertiser id
                  1000001,                  # algorithm id
                  bid2x_var.DEBUG,          # debug flag
                  2,bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,
                  2,bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))
  elif zone.lower() == 'c2':
    app.zone_array.append(
      bid2x_model("Campaign2",              # name
                  10000002,                 # campaign id
                  bid2x_var.ADVERTISER_ID,  # advertiser id
                  1000002,                  # algorithm id
                  bid2x_var.DEBUG,          # debug flag
                  3,bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,
                  3,bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))  
  elif zone.lower() == 'c3':
    app.zone_array.append(
      bid2x_model("Campaign3",              # name
                  10000003,                 # campaign id
                  bid2x_var.ADVERTISER_ID,  # advertiser id
                  1000003,                  # algorithm id
                  bid2x_var.DEBUG,          # debug flag
                  4,bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,
                  4,bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))
  elif zone.lower() == 'c4':
    app.zone_array.append(
      bid2x_model("Campaign4",              # name
                  10000004,                 # campaign id
                  bid2x_var.ADVERTISER_ID,  # advertiser id
                  1000004,                  # algorithm id
                  bid2x_var.DEBUG,          # debug flag
                  5,bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,
                  5,bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))
  elif zone.lower() == 'c5':
    app.zone_array.append(
      bid2x_model("Campaign5",              # name
                  10000005,                 # campaign id
                  bid2x_var.ADVERTISER_ID,  # advertiser id
                  1000005,                  # algorithm id
                  bid2x_var.DEBUG,          # debug flag
                  6,bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,
                  6,bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))

# Take the global variables assigned through the command line arguments and
# copy them to app.* now that they have been created in the previous step.
bid2x_var.assign_vars_to_objects(app)

# If our entrypoint is main then run it.  The function hello_pubsub() is
# the entry point when called through GCP Cloud Functions.
if __name__ == '__main__':
  main(sys.argv)
