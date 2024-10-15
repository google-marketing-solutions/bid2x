"""
  BidToX for SA360 (through GTM)/DV360

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

  This Python application can be used to dynamically create SA360(GTM)/DV360
  Custom Bidding Scipts.

  The SA360 application uses Google Tag Manager custom variable templates as
  scripts to modify bidding multipliers.  There is no direct interfacing
  with SA360.

  The DV360 application can also be used to list custom bidding algorithms,
  create new algorithms, delete custom bidding algorithms, and list custom
  bidding scripts through the use of the -a<X> arguments.

  Overriding the default partner ID, advertiser ID, algorithm ID, debug
  level, index file, JSON authentication file, service account, and tmp
  file location are also all available through various arguments.

  Consult the accompanying 'requirements.txt' file for the list of dependancies.
"""

# Import required libraries & modules
import base64
import sys

from datetime import datetime
from dotenv import load_dotenv
import gspread
import functions_framework

import bid2x_var
from bid2x_env import process_environment_vars
from bid2x_args import process_command_line_args
from bid2x_util import read_config
from bid2x_model import bid2x_model
from bid2x_application import bid2x_application


# Triggered from a message on a Cloud Pub/Sub topic.
# For a deployment on Cloud Functions in GCP this function is the entry point.
@functions_framework.cloud_event
def hello_pubsub(cloud_event) -> None:
    """This function is the entry point for the code when triggered by a
    GCP PubSub call.
    Args:
        cloud_event: a GCP event that is expected to contain data with either
        'update_sheets' or 'upload_cb'.  When the data contains b'update_sheets'
        a known good config for updating the Google Sheet is loaded from an .env
        file which loads environment variables, those vars are copied to the
        bid2x_var scope using the process_environment_vars() call and then
        assign_vars_to_objects() is called to move those values into the app
        object.  When the data contains b'upload_cb' a known good config for
        uploading custom bidding scripts is loaded from an .env file and the
        variables and object readied. Once ready the main() function is called
        to execute the action.
    Returns:
        None.
    """
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
    """
        This is the main function of the script.

        It performs the following actions:

        1. Reads config from a file.
        2. Does one of the following:
            a) [Both DV360 and GTM] Creates the custom bidding script and saves
                it to DV360/GTM.
            b) [DV360-only] Lists all algorithms at an advertiser level.
            c) [DV360-only] Lists all scripts at an advertiser level.
            d) [DV360-only] Create new algorithm at partner level.
            e) [DV360-only] Update reference spreadsheet.
            f) [DV360-only] Remove algorithm.
            g) [DV360-only] Update custom bidding script to reference sheet.

        Example usage:
            python main.py -i="dv_config.json"
    """
    print(f'Bid2X script - Startup  {datetime.now()}')

    try:
        bid2x_var.SPREADSHEET_URL
    except NameError:
        print("No args exist, preload a known good set")
        load_dotenv('./sample-env-vars.env')
        process_environment_vars()

    print(f'Platform Type: {app.platform_type}')

    if app.platform_type == bid2x_var.PlatformType.GTM.value:
        if not app.authenticate_service(app.json_auth_file,
                                        app.service_account_email,
                                        bid2x_var.PlatformType.GTM.value):
            print('Failure on auth to GTM')
            return False

    if app.platform_type == bid2x_var.PlatformType.DV.value:
        if not app.authenticate_service(app.json_auth_file,
                                        app.service_account_email,
                                        bid2x_var.PlatformType.DV.value):
            print('Failure on auth to DV')
            return False

    if not app.authenticate_service(app.json_auth_file,
                                    app.service_account_email,
                                    bid2x_var.PlatformType.SHEETS.value):
        print('Failure on auth to Sheets')
        return False

    print(f'Starting sheets_service check {app.sheet.sheets_service}')
    if not app.sheet.sheets_service:
        print('Error authenticating sheets using provided JSON information')
        return False

    print('Start-up Configuration:')
    print(app)

    # Is 'service' (i.e. a conntection to DV360) valid?
    # If yes then proceed to process actions.
    if app.service:
        app.run_script()

    else:
        print('Unable to connect to service; no service - stopped')
        return False

    print(f'Bid2X script - Finished {datetime.now()}')
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

# If an input file is passed as an argument then bid2x_var.INPUT_FILE will
# be set and will not be 'None' (the default).  If this is the case follow
# the steps in this if construct to create new objects and load the config
# into them.
if bid2x_var.INPUT_FILE:
    # Start with default app object.
    print(f'Input file is: {bid2x_var.INPUT_FILE}')
    app = bid2x_application(
        bid2x_var.API_SCOPES,
        bid2x_var.API_NAME,
        bid2x_var.API_VERSION,
        bid2x_var.SPREADSHEET_KEY,
        bid2x_var.JSON_AUTH_FILE,
        bid2x_var.PLATFORM_TYPE)
    # Then read input file into new object.
    stored_app = read_config(bid2x_var.INPUT_FILE)

    # Update all values in app object with newly read values.

    # Copy 'sheet' sub-object items to app.
    if 'sheet' in stored_app:
        app.platform_type = stored_app['platform_type']
        app.sheet.top_level_copy(source=stored_app['sheet'], platform_type=app.platform_type)

        if not app.platform_object:
            app.start_service()

    if stored_app['platform_type'] == bid2x_var.PlatformType.DV.value and 'zone_array' in stored_app:
        # Remove all previous zones first.
        app.zone_array = []

        # Walk loaded zones and recreate with new model objects.
        for zone in stored_app['zone_array']:
            app.platform_object.zone_array.append(
                bid2x_model(zone['name'],
                            zone['campaign_id'],
                            zone['advertiser_id'],
                            zone['algorithm_id'],
                            zone['debug'],
                            zone['update_row'],
                            zone['update_col'],
                            zone['test_row'],
                            zone['test_col']))

    # Finally, update main app with loaded values.
    app.top_level_copy(stored_app)

    # Re-initialize dv_service (not saved in JSON).
    if app.platform_type == bid2x_var.PlatformType.DV.value and \
          not app.auth.auth_dv_service(app.json_auth_file,
                                      app.service_account_email):
        print('Failure on auth to DV')

    # Re-initialize sheets_service (not saved in JSON).
    if not app.auth.auth_sheets(app.sheet.json_auth_file,
                                app.service_account_email):
        print('Failure on auth to Sheets')

    # Re-initialize gc (gspread) object (not saved in JSON)
    app.sheet.gc = gspread.service_account(filename=app.sheet.json_auth_file)

# This branch is used when NO input file is passed and we need to create
# an app object with defaults.
else:
    # No config file passed, use the defaults.
    app = bid2x_application(
        bid2x_var.API_SCOPES,
        bid2x_var.API_NAME,
        bid2x_var.API_VERSION,
        bid2x_var.SPREADSHEET_KEY,
        bid2x_var.JSON_AUTH_FILE,
        bid2x_var.PLATFORM_TYPE)

    app.zone_array = []

    if bid2x_var.ZONES_TO_PROCESS is None:
        bid2x_var.ZONES_TO_PROCESS = 'c1,c2,c3,c4,c5'
    zone_list = bid2x_var.ZONES_TO_PROCESS.split(",")

    # Populate the default app with the default number of zones / campaigns.
    i=1
    for zone in zone_list:
        app.zone_array.append(
            bid2x_model(f"Campaign_{zone}",                       # name
                        bid2x_var.DEFAULT_MODEL_CAMPAIGN_ID+i,    # campaign id
                        bid2x_var.ADVERTISER_ID,                  # advertiser id
                        bid2x_var.DEFAULT_MODEL_ALGORITHM_ID+i,   # algorithm id
                        bid2x_var.DEBUG,                          # debug flag
                        bid2x_var.DEFAULT_MODEL_SHEET_ROW+1,      # sheet row update
                        bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,   # sheet col update
                        bid2x_var.DEFAULT_MODEL_SHEET_ROW+1,      # sheet row test,
                        bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST))    # sheet col test
        i+=1

    # Take the global variables assigned through the command line arguments and
    # copy them to app.* now that they have been created in the previous step.
    bid2x_var.assign_vars_to_objects(app)

# If our entrypoint is main then run it.  The function hello_pubsub() is
# the entry point when called through GCP Cloud Functions.
if __name__ == '__main__':
    main(sys.argv)
