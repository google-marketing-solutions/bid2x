"""BidToX - Automated custom bidding for SA360/GTM and DV360.

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

  Consult the accompanying 'requirements.txt' file for the list of dependencies.
"""

# Import required libraries & modules
import base64
import datetime
import json
import sys
from typing import Any

import bid2x_application
from bid2x_application import Bid2xApplication
from bid2x_args import process_command_line_args
from bid2x_gtm_model import Bid2xGTMModel
from bid2x_model import Bid2xModel
import bid2x_util as util
import bid2x_var
import functions_framework
import gspread


# Triggered from a message on a Cloud Pub/Sub topic.
# For a deployment on Cloud Functions in GCP this function is the entry point.
@functions_framework.cloud_event
def hello_pubsub(cloud_event: Any) -> None:
  """Function to act as the entry point for the code when triggered by PubSub.

  Args:
      cloud_event: a GCP event that is expected to contain data with the
      name of a file to be loaded.  The file is a JSON file already
      deployed in the cloud function containing a pre-configured set
      of functionality.  An example would be a file used to update all
      zones by creating new custom bidding scripts and uploading to DV360.
      Another example might be to update the spreadsheet with new data
      for a zone or two.
      Once ready the main() function is called to execute the action.
  Returns:
      None.
  """

  global app

  # Extract the filename from the message data.
  message_data = cloud_event.data['message']['data']
  filename = base64.b64decode(message_data).decode('utf-8')

  # The message passed in the Pub/Sub message is the JSON filename to
  # load and execute.
  app = create_objects_from_json_file(filename)

  # At the moment this assumes the passed filename is a local file.
  # This needs to be extended such that the config file can be
  # located elsewhere.

  # Now run the main loop.
  main(sys.argv)


def main(argv: Any) -> int:
  """This is the main function of the script.

  Args:
      argv: The command line arguments.
  Returns:
      True if the main loop completed successfully.
      False if there was an error or failure.

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
          python main.py -i=dv_config.json
  """
  global app

  current_datetime = datetime.datetime.now()
  print(f'bid2x - Startup  {current_datetime} with argv: {argv}')
  try:
    bid2x_var.SPREADSHEET_URL
  except NameError:
    print('No args exist, preload a known good set')
    app = create_objects_from_json_file('sample_config.json')

  if app.platform_type == bid2x_var.PlatformType.DV.value:
    # This is a DV service.
    if not app.auth.auth_dv_service(
        app.json_auth_file, app.service_account_email
    ):
      print('Failure on auth to DV')
      return -1
  elif app.platform_type == bid2x_var.PlatformType.GTM.value:
    # This is a GTM/SA service.
    if not app.auth.auth_gtm_service(
        app.json_auth_file, app.service_account_email
    ):
      print('Failure on auth to GTM')
      return -1

  if not app:
    print('App object not valid - exiting...')
    return -1
  else:
    print('Start-up Configuration:')
    print(f'{app}')

  # Is this a DV360 type connection?
  if app.platform_type == bid2x_var.PlatformType.DV.value:

    if app.platform_object.action_list_scripts:
      # Show advertiser level scripts for each initialized zone.
      for zone in app.zone_array:
        response = app.platform_object.list_advertiser_algo_scripts(
            app.service, zone.advertiser_id
        )
        if app.debug:
          print(
              f'Custom bidding scripts for zone {zone.name}',
              f' advertiser_id = {zone.advertiser_id}',
          )
          json_pretty_print = json.dumps(response, indent=2)
          print(f'{json_pretty_print}')

    if app.platform_object.action_list_algos:
      # Show advertiser level algorithms for each initialized zone.
      response = app.platform_object.list_advertiser_algorithms(
          app.service, app.platform_object.advertiser_id
      )
      if app.trace:
        print(
            'Advertiser level algorithms for advertiser ID ',
            f'= {app.platform_object.advertiser_id}',
        )
        json_pretty_print = json.dumps(response, indent=2)
        print(f'{json_pretty_print}')

    if app.platform_object.action_create_algorithm:
      # Create a new custom bidding algorithm from Partner level.
      print('Create new custom bidding algorithm for zone(s):')

      for zone in app.zone_array:
        # Create CB Algorithm at the Advertiser level.
        algorithm_name = app.platform_object.new_algo_name + '_' + zone.name
        display_name = (
            app.platform_object.new_algo_display_name + '_' + zone.name
        )
        print(f'New algorithm name: {display_name}')
        response = app.platform_object.create_cb_algorithm_advertiser(
            app.service, app.platform_object.advertiser_id, algorithm_name,
            display_name
        )

        if app.trace:
          json_pretty_print = json.dumps(response, indent=2)
          print(f'new custom bidding algorithm response = {json_pretty_print}')

    if app.platform_object.action_remove_algorithm:
      # Remove an advertiser custom bidding algorithm by ID.
      print(
          f'Custom bidding algorithm id {app.platform_object.cb_algo_id} ',
          'will be attempted to be deleted.',
      )
      response = app.platform_object.remove_cb_algorithm_advertiser(
          app.service,
          app.platform_object.advertiser_id,
          app.platform_object.cb_algo_id,
      )

      print(f'result of deletion attempt: {response}')

    if app.platform_object.action_update_scripts:
      # Update the custom bidding scripts in DV360.

      # Create custom bidding script for DV360 as a string - per sales zone.
      for zone in app.zone_array:
        # Go into Google Sheets and generate CB function per sales zone.
        custom_bidding_function_string = (
            app.platform_object.generate_cb_script_max_of_conversion_counts(
                zone.name
            )
        )

        if app.trace:
          # Show the generated custom bidding script.
          print(
              'custom_bidding_function_string:\n',
              f'{custom_bidding_function_string}\n',
          )

        # Get a list of line items this will affect.
        line_item_array = app.sheet.get_affected_line_items_from_sheet(
            zone.name
        )
        # Get the current algorithm directly from DV360.
        custom_bidding_current_script = (
            app.platform_object.read_cb_algorithm_by_id(
                app.service,
                app.platform_object.advertiser_id,
                zone.algorithm_id,
            )
        )

        if app.trace:
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
        filename = (
            app.platform_object.cb_tmp_file_prefix + '_' + zone.name + '.txt'
        )
        # Compare the new script and the previously uploaded script.
        if (
            str(custom_bidding_function_string).strip() ==
            str(custom_bidding_current_script).strip()
        ):

          # The new script is the same as the old script, don't write to file
          # and don't upload.  Just return False from this function.
          print('New script is the same as the existing script; not uploading')

          # Go to next item in outer loop.
          continue
        else:
          print(
              'New script is different from last ',
              'uploaded script; uploading new version.',
          )

          # Write new script to tmp filename.  Upload is from a tmp file.
          app.platform_object.write_last_upload_file(
              filename, custom_bidding_function_string
          )

          # Make call to update script in DV360 passing in filename containing
          # new script.
          update_result = zone.update_custom_bidding_scripts(
              app.service,
              zone.advertiser_id,
              zone.algorithm_id,
              filename,
              line_item_array,
          )

          if not update_result:
            print(f'Update of C.B. Script for zone {zone.name} failed.')
          else:
            print(f'Update of C.B. Script for zone {zone.name} succeeded.')
            # Update of C.B. script was successful, update the Google
            # Sheets spreadsheet tab named 'CB_Scripts' (by default).
            app.sheet.update_cb_scripts_tab(
                zone, custom_bidding_function_string, test_run=False
            )

    if app.platform_object.action_test:
      for zone in app.zone_array:
        # Generate the Custom Bidding Script.
        custom_bidding_string = (
            app.platform_object.generate_cb_script_max_of_conversion_counts(
                zone.name
            )
        )
        # Write the Test Run out to the test column in the associated
        # Google Sheet in the tab 'CB_Scripts'.
        app.sheet.update_status_tab(
            'CB_Scripts', zone, custom_bidding_string, test_run=True
        )

        if app.trace:
          # Print the value of the script to the console - since this runs
          # typically as a Cloud Function then this will end up in the logs.
          print(
              f"""rules for zone {zone.name}:\n
                {custom_bidding_string}"""
          )

    if app.platform_object.action_update_spreadsheet:
      app.sheet.read_dv_line_items(
          app.service,
          app.platform_object.line_item_name_pattern,
          app.zone_array,
          app.platform_object.defer_pattern,
      )

  # Do we have a service object and are we dealing with a GTM object?
  elif app.platform_type == bid2x_var.PlatformType.GTM.value:

    if app.platform_object.action_update_scripts:
      app.platform_object.process_script(
          app.service, app.zone_array, test_flag=False
      )
    elif app.platform_object.action_test:
      app.platform_object.process_script(
          app.service, app.zone_array, test_flag=True
      )
  else:
    print('Unable to connect to service object - stopped')
    return -1

  current_datetime = datetime.datetime.now()
  print(f'bid2x - Finished {current_datetime}')
  return 0


def create_objects_from_json_file(filename: str) -> Bid2xApplication:
  """Create app object from a JSON file.

  Args:
      filename: The name of the JSON file to load.
  Returns:
      The created app object.
  """

  global app

  if filename:
    # Start with default app object.
    # Then read input file into new object.
    stored_app = util.read_config(filename)

    # Determine what type of system this config file is for.
    if stored_app['platform_type'] and (
        stored_app['platform_type'].upper() in ('DV', 'GTM')
    ):

      app = Bid2xApplication(
          stored_app['scopes'],
          stored_app['api_name'],
          stored_app['api_version'],
          stored_app['sheet']['sheet_id'],
          stored_app['json_auth_file'],
          stored_app['platform_type'].upper(),
      )
    else:
      print('Invalid platform type')
      return  # Or should this be an immediate exit?

    app.start_service()

    # Update all values in app object with newly read values.
    # Copy 'sheet' sub-object items to app.
    if 'sheet' in stored_app:
      app.sheet.top_level_copy(
          stored_app['sheet'], stored_app['platform_type'].upper()
      )

    if 'zone_array' in stored_app:
      # Remove all previous zones first.
      app.zone_array = []

      # Walk loaded zones and recreate with new model objects.
      for zone in stored_app['zone_array']:

        if app.platform_type == bid2x_var.PlatformType.DV.value:
          app.zone_array.append(
              Bid2xModel(
                  zone['name'],
                  zone['campaign_id'],
                  zone['advertiser_id'],
                  zone['algorithm_id'],
                  zone['debug'],
                  zone['update_row'],
                  zone['update_col'],
                  zone['test_row'],
                  zone['test_col'],
              )
          )
        elif app.platform_type == bid2x_var.PlatformType.GTM.value:
          app.zone_array.append(
              Bid2xGTMModel(
                  zone['name'],
                  zone['account_id'],
                  zone['container_id'],
                  zone['workspace_id'],
                  zone['variable_id'],
                  zone['update_row'],
                  zone['update_col'],
                  zone['test_row'],
                  zone['test_col'],
              )
          )

    # Finally, update main app with loaded values.
    app.top_level_copy(stored_app)

    if not app.authenticate_service(
        app.json_auth_file, app.service_account_email, app.platform_type
    ):
      print('Failure on auth sub-service')

    # Re-initialize gc (gspread) object (not saved in JSON).
    app.sheet.gc = gspread.service_account(filename=app.sheet.json_auth_file)

  else:
    # This branch is used when NO input file is passed and we need to create
    # an app object with defaults.
    app = Bid2xApplication(
        bid2x_var.API_SCOPES,
        bid2x_var.API_NAME,
        bid2x_var.API_VERSION,
        bid2x_var.SPREADSHEET_KEY,
        bid2x_var.JSON_AUTH_FILE,
        str(bid2x_var.PLATFORM_TYPE).upper(),
    )

    # No config file passed, use the defaults.
    app.zone_array = []

    if bid2x_var.ZONES_TO_PROCESS is None:
      bid2x_var.ZONES_TO_PROCESS = 'c1,c2,c3,c4,c5'
    zone_list = bid2x_var.ZONES_TO_PROCESS.split(',')

    # Populate the default app with the default number of zones / campaigns.
    i = 1
    for zone in zone_list:
      if app.platform_type == bid2x_var.PlatformType.DV.value:
        app.zone_array.append(
            Bid2xModel(
                f'Campaign_{zone}',  # name
                bid2x_var.DEFAULT_MODEL_CAMPAIGN_ID + i,  # campaign id
                bid2x_var.ADVERTISER_ID,  # advertiser id
                bid2x_var.DEFAULT_MODEL_ALGORITHM_ID + i,  # algorithm id
                bid2x_var.DEBUG,  # debug flag
                bid2x_var.DEFAULT_MODEL_SHEET_ROW + 1,  # sheet row update
                bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,  # sheet col update
                bid2x_var.DEFAULT_MODEL_SHEET_ROW + 1,  # sheet row test
                bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST  # sheet col test
            )
        )
      elif app.platform_type == bid2x_var.PlatformType.GTM.value:
        app.zone_array.append(
            Bid2xGTMModel(
                f'GTM_{zone}',  # name
                bid2x_var.GTM_ACCOUNT_ID,  # account id
                bid2x_var.GTM_CONTAINER_ID,  # container id
                bid2x_var.GTM_WORKSPACE_ID,  # workspace id
                bid2x_var.GTM_VARIABLE_ID + i,  # variable id
                bid2x_var.DEFAULT_MODEL_SHEET_ROW + 1,  # sheet row update
                bid2x_var.DEFAULT_CB_SCRIPT_COL_UPDATE,  # sheet col update
                bid2x_var.DEFAULT_MODEL_SHEET_ROW + 1,  # sheet row test
                bid2x_var.DEFAULT_CB_SCRIPT_COL_TEST  # sheet col test
            )
        )
      i += 1

    # Take the global variables assigned through the command line arguments and
    # copy them to app.* now that they have been created in the previous step.
    app.assign_vars_to_objects()

  return app


# Walk sys.argv using argparse to process passed arguments.
# The use of command line arguments is meant for development or for
# running the system from the command line.
process_command_line_args()

app: bid2x_application.Bid2xApplication = None
# Create objects based on passed file.
app = create_objects_from_json_file(bid2x_var.INPUT_FILE)

# If our entrypoint is main then run it.  The function hello_pubsub() is
# the entry point when called through GCP Cloud Functions.
if __name__ == '__main__':
  main(sys.argv)
