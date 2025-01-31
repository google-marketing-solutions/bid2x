"""BidToX - bid2x_gtm application module.

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

  This module contains the bid2x_gtm class which is used to process
  the GTM platform.
"""

import datetime
from typing import Any

from bid2x_platform import Platform
import bid2x_spreadsheet
import bid2x_var
import pandas as pd


class Bid2xGTM(Platform):
  """GTM object for custom variable template bidding script.

  Attributes:
      sheet (bid2x_spreadsheet): Reference data for index and
          bid factor and rules.
      index_filename(str): Name of the referenced sheet.
      index_tab_name(str): Name of index tab.
      value_adjustment_tab_name(str): Name of the bidding factor tab.
      debug(bool): Flag for debug mode.
      account_id(str): GTM account id of the script.
      container_id(str): GTM container id of the script.
      workspace_id(str): GTM workspace id of the script.
      variable_id(str): GTM variable id of the script.

  Methods:
      mapping_data(self, input_df, value_adjustment_df):
          Walks the passed dataframe, compares the INDEX_FACTOR
          column against predefined values and sets a value
          adjustment.
      print_dataframe(self, input_df):
          Converts a dataframe to a string and prints it to stdout.
      read_sheets_data(self):
          Read the sheets data to get the index information for each
          row and map it to another tab in the sheet with index range
          and the bid modifier for each range.
      write_javascript_function (self, input_df):
          Given a Dataframe created from a provided Google Sheets file,
          this function creates a string containing a JavaScript
          function for use in Google Tag Manager.
      update_gtm_variable(self, service, new_function):
          This function updates a variable within the Google Tag Manager
          using the value in the 'new_function' parameter.
      process_script(self, service):
          This function orchestrates the custom variable change in GTM
          that adjusts bid multipliers for different routes by way of a
          custom script that is saved into the custom variable.
      top_level_copy(self, source): Copies all variable settings
      from config file to the object.
  """
  sheet: bid2x_spreadsheet
  index_filename: str
  index_tab_name: str
  value_adjustment_tab_name: str
  debug: bool = False
  account_id: str
  container_id: str
  workspace_id: str
  variable_id: str

  def __init__(self,
               sheet: bid2x_spreadsheet,
               debug: bool) -> None:
    self.sheet = sheet
    self.index_filename = 'test_filename'
    self.index_tab_name = 'test_tab'
    self.value_adjustment_tab_name = 'value_adjustment_tab_name'
    self.account_id = 0
    self.container_id = 0
    self.workspace_id = 0
    self.variable_id = 0
    self.debug = debug

  def __str__(self)->str:
    """Override str method to return a sensible string.

    Args:
        None.

    Returns:
        A formatted string containing a formatted list of object properties.
    """
    return_str = (f'index_filename: {self.index_filename}\n' +
                  f'index_tab_name: {self.index_tab_name}\n' +
                  'value_adjustment_tab_name: ' +
                  f'{self.value_adjustment_tab_name}\n' +
                  f'account_id: {self.account_id}\n' +
                  f'container_id: {self.container_id}\n' +
                  f'workspace_id: {self.workspace_id}\n' +
                  f'variable_id: {self.variable_id}\n')

    return return_str

  def mapping_data(self, input_df: pd.DataFrame,
                   value_adjustment_df: pd.DataFrame) -> pd.DataFrame:
    """Walks dataframe and sets a value adjustment.

    Args:
      input_df: dataframe from loading client supplied index file.
      value_adjustment_df: dataframe from loading client supplied value
          adjustment file.

    Returns:
      An updated dataframe now with a value_adjustment column of
      float numbers.
    """

    # Reads list of range and value adjustments per sheet.
    df = input_df.reset_index()  # make sure indexes pair with # of rows.
    values_df = value_adjustment_df.reset_index()

    df[bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value] = (
        1.0  # set default calculated value to 1.0.
    )

    # Iterates through all rows from the index tab's INDEX_FACTOR column
    # and compares it against the value_adjustments tab's low and high
    # index values in each row.  If it finds that the INDEX_FACTOR value
    # in the row matches one of the bounds of the low and high index
    # values, it will replace the value_adjustment column for the index
    # file's current row with the new bid multiplier.
    for i_index, i_row in df.iterrows():
      for row in values_df.iterrows():
        if (
            i_row[bid2x_var.GTMColumns.INDEX_FACTOR.value]
            <= row[bid2x_var.GTMColumns.INDEX_HIGH.value]
            and i_row[bid2x_var.GTMColumns.INDEX_FACTOR.value]
            > row[bid2x_var.GTMColumns.INDEX_LOW.value]
        ):

          df.at[i_index, bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value] = row[
              bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value
          ]

    return df

  def print_dataframe(self, input_df: pd.DataFrame) -> None:
    """Converts a dataframe to a string and prints it to stdout.

    Args:
      input_df: any dataframe.

    Returns:
      None.
    """
    # make sure indexes pair with number of rows
    df = input_df.reset_index()

    if self.debug:
      print(df.to_string())

  # Function to automate data imports, data processing, mapping
  # and opportunity calculation
  def read_sheets_data(self) -> pd.DataFrame:
    """Read sheet data for access to index info.

    Args:
      None.

    Returns:
      An updated dataframe now with a value_adjustment column of
      float numbers.
    """

    # load index data file
    spreadsheet = self.sheet.gc.open(self.index_filename)

    index_tab = spreadsheet.worksheet(self.index_tab_name)
    value_adjustment_tab = spreadsheet.worksheet(self.value_adjustment_tab_name)

    index_data = index_tab.get_all_values()
    index_df = pd.DataFrame(index_data[1:], columns=index_data[0])

    value_adjustment_data = value_adjustment_tab.get_all_values()
    value_adjustment_df = pd.DataFrame(value_adjustment_data[1:],
                                       columns=value_adjustment_data[0])

    if self.debug:
      print('Index DataFrame as read in:')
      self.print_dataframe(index_df)

      print('Value Adjustment DataFrame as read in:')
      self.print_dataframe(value_adjustment_df)

    # expected file format (including header):
    #    LEG_SCHD_ORIG	LEG_SCHD_DEST	CMCL_SERV_NAME	INDEX_FACTOR
    #    DCA	YYZ	US	0.2036064711
    #    HKG	YVR	PACIFIC	0.6338395037
    #    LIS	YUL	ATLANTIC	0.9499136993
    #    MCO	YUL	US	0.8733527455
    #    ORD	YYZ	US	0.5722639361
    #    SFO	YEG	US	0.2033802793
    #    YCG	YVR	CANADA	0.7851325037
    # ...

    # Run index DataFrame through mapping_data process to convert index
    # value to a multiplier based on the range.  This adds a column to the
    # index DataFrame called 'value_adjustment' and is currently based on
    # another tab in the same sheets file similar the following lookup
    # table:
    #     index_low      index_high      value_adjustment
    #        0.8            100              1.0  (i.e. no change)
    #        0.6            0.8              1.2  (i.e. 20% lift)
    #        0.3            0.6              1.4  (i.e. 40% lift)
    #        100            0.3              1.6  (i.e. 60% lift)
    index_df = self.mapping_data(index_df, value_adjustment_df)

    return index_df

  def write_javascript_function(self, input_df: pd.DataFrame) -> str:
    """Creates a string containing a JavaScript function for use in GTM.

    Args:
        input_df: dataframe from loading client supplied index file.

    Returns:
        A string representation of a JavaScript function for use
        with GTM to be loaded into a variable there.
    """

    # Set the first part of the function for GTM
    js_function_string_start = """function() {
    var origDestRevenue = {{Pixel-Transaction-TotalCAD}};\n"""

    # Create the repeating part of the function string by
    # starting with a blank string
    js_function_string_middle = ''

    # Walk the passed dataframe a row at a time
    for i, irow in input_df.iterrows():
      # extract the origin, destination, and adjustment factor
      # from the current row of the dataframe
      org = irow[bid2x_var.GTMColumns.ORIGIN.value]
      dst = irow[bid2x_var.GTMColumns.DESTINATION.value]
      adj = irow[bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value]

      # If this is the first clause (row 0) there is no 'else'
      # otherwise this is the continuation of an if-statement
      # and use 'else ' to continue the statement
      if i > 0:
        clause_prefix = 'else '
      else:
        clause_prefix = ''

      # Create a JavaScript comparison between the current origin and
      # destination and those values provided in the passed Dataframe.
      # If the origin and destination match the IATA codes then set a
      # tag variable 'origDestRevenue' to the original transaction fee
      # multiplied by the multiplication factor, also contained within
      # the passed dataframe
      js_function_string_middle += f'  {clause_prefix}if ('
      js_function_string_middle += '{{Pixel-flight-depart-origin}} == '
      js_function_string_middle += f"'{org}' && "
      js_function_string_middle += '{{Pixel-flight-depart-destination}} == '
      js_function_string_middle += f"'{dst}') "
      js_function_string_middle += '{\n'
      js_function_string_middle += (
          '    origDestRevenue = {{Pixel-Transaction-TotalCAD}} * ')
      js_function_string_middle += f'{adj}; '
      js_function_string_middle += '}\n'

    # Define the end of the function
    js_function_string_end = ' return origDestRevenue; }'

    # Assemble the JavaScript function
    js_function_string = (
        js_function_string_start +
        js_function_string_middle +
        js_function_string_end)

    # Return the finalized JavaScript function for use in GTM
    return js_function_string

  # Update the variable using GTM API
  def update_gtm_variable(self, service: Any, new_function: str) -> bool:
    """Update Google Tag Manager variable with new JavaScript function.

    Args:
        service: a service object previously opened with the GTM API.
        new_function: a string containing the value to update within the
          variable_id.

    Returns:
        The function returns True upon successful update or False if
        it was unable to update the variable.
    """

    # Create a new workspace version to operate on
    prod_workspace_path = (
        f'accounts/{self.account_id}/containers/{self.container_id}'
    )

    now = datetime.now()
    datetime_string = now.strftime('%d/%m/%Y %H:%M:%S')
    datetime_string_simplified = now.strftime('%Y%m%d%H%M%S')

    gtm_body_name = f'Copy of production {datetime_string_simplified}'
    gtm_body_notes = (
        f'Auto-generated workspace - made in GTM API - {datetime_string}'
    )
    gtm_new_workspace_body = {'name': gtm_body_name, 'notes': gtm_body_notes}

    if self.debug:
      print(f'gtm_new_workspace_body: {gtm_new_workspace_body}')
      print(f'prod_workspace_path: {prod_workspace_path}')

    gtm_new_workspace = (
        service.accounts()
        .containers()
        .workspaces()
        .create(parent=prod_workspace_path, body=gtm_new_workspace_body)
        .execute()
    )

    # return value of call to create new workspace gives new ids - use them:
    if gtm_new_workspace and gtm_new_workspace['fingerprint']:
      account_id = gtm_new_workspace['accountId']
      container_id = gtm_new_workspace['containerId']
      workspace_id = gtm_new_workspace['workspaceId']

      if self.debug:
        print(f'gtm_new_workspace return value: {gtm_new_workspace}')

    else:
      return False

    # Build the path for getting / updating the variable using the passed args
    var_req = (
        f'accounts/{account_id}/containers/{container_id}/'
        f'workspaces/{workspace_id}/variables/{self.variable_id}'
    )

    # get the current value of the variable in GTM
    gtm_var = (
        service.accounts()
        .containers()
        .workspaces()
        .variables()
        .get(path=var_req)
        .execute()
    )

    if self.debug:
      print(f'GTM var is: {gtm_var}')
      print(f'Current internal function is{gtm_var["parameter"][0]["value"]}')

    # set gtm_var holder to have new value of function that was passed
    gtm_var['parameter'][0]['value'] = new_function

    if self.debug:
      print(f'GTM var after update is: {gtm_var}')
      print(f'Proposed internal function is{gtm_var["parameter"][0]["value"]}')

    # Update GTM with the new version of gtm_var that has been updated
    # with the new JavaScript function
    gtm_updated = (
        service.accounts()
        .containers()
        .workspaces()
        .variables()
        .update(path=var_req, body=gtm_var)
        .execute()
    )

    if self.debug:
      print(f'return value from update on GTM is: {gtm_updated}')

    # Check to see if the value returned for the variable's value is the
    # same as what it was passed.  This indicates a successful update.
    if gtm_updated['parameter'][0]['value'] == gtm_var['parameter'][0]['value']:
      if self.debug:
        print('Update variable success')

    else:
      # not a good return value, return from function
      return False

    # Prep for versioned workspace
    gtm_path = (
        f'accounts/{account_id}/containers/{container_id}/'
        f'workspaces/{workspace_id}'
    )
    gtm_name = f'Auto-versioned container {datetime_string_simplified}'
    gtm_notes = (
        f'This container auto-versioned on {datetime_string} using GTM API'
    )
    gtm_versioned_workspace_body = {'name': gtm_name, 'notes': gtm_notes}

    if self.debug:
      print('Create_version()... ')
      print(f'gtm_path = {gtm_path}')
      print(f'gtm_versioned_workspace_body = {gtm_versioned_workspace_body}')

    # Created versioned workspace
    gtm_versioned_workspace = (
        service.accounts()
        .containers()
        .workspaces()
        .create_version(path=gtm_path, body=gtm_versioned_workspace_body)
        .execute()
    )

    if gtm_versioned_workspace:
      # get version ID here and save to variable for use wuth publish
      version_id = gtm_versioned_workspace['containerVersion'][
          'containerVersionId'
      ]

      if self.debug:
        print(f'gtm_versioned_workspace: {gtm_versioned_workspace}')
        print('new version success')
    else:
      return False

    # Prep for publish command
    gtm_publish_path = (
        f'accounts/{account_id}/containers/{container_id}/versions/{version_id}'
    )
    gtm_published = (
        service.accounts()
        .containers()
        .versions()
        .publish(
            path=gtm_publish_path,
        )
        .execute()
    )

    # check return value of gtm_publish_path
    if gtm_published:
      if self.debug:
        print(f'gtm_published: {gtm_published}')
    else:
      return False

    return True

  # Starts the data reading and custom bidding process
  def process_script(self, service: Any) -> bool:
    """Orchestrates the variable change in GTM.

    Args:
      service: A service object previously opened with the GTM API.

    Returns:
      True if process is a success.  False otherwise.
    """

    # Read the index data from a spreadsheet into a Dataframe
    index_df = self.read_sheets_data()

    # print finailized DataFrame that was read in and processed
    if self.debug:
      self.printDataFrame(index_df)

    # jsFunctionString = writeJavaScriptFunction(index_df)
    js_function = self.write_javascript_function(index_df)

    if self.debug:
      print(f'generated js function returned: {js_function}')

    # if there's a good service and a good function update the GTM variable
    if service and js_function:
      if self.debug:
        print(f'service: {service}')
        print(f'account_id: {self.account_id}')
        print(f'container_id: {self.container_id}')
        print(f'workspace_id: {self.workspace_id}')
        print(f'variable_id: {self.variable_id}')
        print(f'js_function: {js_function}')

      ret_val = self.update_gtm_variable(
          service,
          js_function)

      if ret_val:
        print(f'Success updating GTM variable to new value of:{chr(10)}',
              f'{js_function}')
      else:
        print('Error updating GTM variable with function')
        return False
    else:
      print('No service to connect with.')
      return False

    return True

  def top_level_copy(self, source: Any) -> None:
    """Copy all config file GTM settings to this object.

    Args:
      source: The config file opened and decoded into readable format.

    Returns:
      None.
    """
    self.debug = source['debug']

    self.account_id = source['gtm_account_id']
    self.container_id = source['gtm_container_id']
    self.workspace_id = source['gtm_workspace_id']
    self.variable_id = source['gtm_variable_id']
    self.index_filename = source['gtm_index_filename']
    self.index_tab_name = source['gtm_index_tab']
    self.value_adjustment_tab_name = source['gtm_value_adjustment_tab']
