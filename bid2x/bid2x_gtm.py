"""BidToX - bid2x_gtm application module.

  Copyright 2025 Google LLC

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
import functools
import json
import re
from typing import Any, Sequence

from bid2x_gtm_model import Bid2xGTMModel
from bid2x_platform import Platform
from bid2x_spreadsheet import Bid2xSpreadsheet
import bid2x_var
import pandas as pd

partial = functools.partial


class GTMFloodlight:
  """GTM Floodlight object.

  Attributes:
      floodlight_name(str): Name of the floodlight.
      per_row_condition(str): Condition to be met for the row.
      total_var(str): Variable name for the total value.
      floodlight_condition(str): Condition to identify the floodlight.
  """
  floodlight_name: str
  per_row_condition: str
  total_var: str
  floodlight_condition: str

  def __init__(
      self,
      floodlight_name: str,
      per_row_condition: str,
      total_var: str,
      floodlight_condition: str | None = None,
  ) -> None:
    self.floodlight_name = floodlight_name
    self.per_row_condition = per_row_condition
    self.total_var = total_var
    self.floodlight_condition = floodlight_condition

  def __str__(self) -> str:
    return_str = (
        f'floodlight_name: {self.floodlight_name}\n'
        f'per_row_condition: {self.per_row_condition}\n'
        f'total_var: {self.total_var}\n'
        f'floodlight_condition: {self.floodlight_condition}\n'
    )

    return return_str


class Bid2xGTM(Platform):
  """GTM object for custom variable template bidding script.

  Attributes:
      sheet (bid2x_spreadsheet): Reference data for index and
          bid factor and rules.
      index_filename(str): Name of the referenced sheet.
      index_tab_name(str): Name of index tab.
      value_adjustment_tab_name(str): Name of the bidding factor tab.
      debug(bool): Flag for debug mode.
      trace(bool): Flag for trace mode.
      account_id(str): GTM account id of the script.
      container_id(str): GTM container id of the script.
      workspace_id(str): GTM workspace id of the script.
      variable_id(str): GTM variable id of the script.

  Methods:
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
  sheet: Bid2xSpreadsheet
  zone_array = list[Any]

  debug: bool = False
  trace: bool = False
  gtm_floodlight_list: list[GTMFloodlight]
  gtm_preprocessing_script: str
  gtm_postprocessing_script: str
  value_adjustment_column_name: str
  index_low_column_name: str
  index_high_column_name: str
  action_update_scripts: bool
  action_test: bool
  zones_to_process: str  # Zones involved in the bidding script.

  def __init__(self, sheet: Bid2xSpreadsheet, debug: bool) -> None:
    self.sheet = sheet
    self.zone_array = []
    self.value_adjustment_tab_name = 'value_adjustment_tab_name'
    self.debug = debug
    self.trace = False
    self.action_update_scripts = False
    self.action_test = True
    self.gtm_floodlight_list = bid2x_var.GTM_FLOODLIGHT_LIST
    self.gtm_preprocessing_script = bid2x_var.GTM_PREPROCESSING_SCRIPT
    self.gtm_postprocessing_script = bid2x_var.GTM_POSTPROCESSING_SCRIPT
    self.value_adjustment_column_name = (
        bid2x_var.GTMColumns.VALUE_ADJUSTMENT.value
    )
    self.index_factor_column_name = bid2x_var.GTMColumns.INDEX_FACTOR
    self.index_low_column_name = bid2x_var.GTMColumns.INDEX_LOW
    self.index_high_column_name = bid2x_var.GTMColumns.INDEX_HIGH

    self.zones_to_process = bid2x_var.ZONES_TO_PROCESS

  def __str__(self) -> str:
    """Override str method to return a sensible string.

    Args: None.

    Returns:
        A formatted string containing a formatted list of object properties.
    """
    return_str = (
        'value_adjustment_tab_name: '
        f'{self.value_adjustment_tab_name}\n'
        f'debug: {self.debug}\n'
        f'trace: {self.trace}\n'
        f'gtm_preprocessing_script: {self.gtm_preprocessing_script}\n'
        f'gtm_postprocessing_script: {self.gtm_postprocessing_script}\n'
        f'index_factor_column_name: {self.value_adjustment_column_name}\n'
        f'index_low_column_name: {self.index_low_column_name}\n'
        f'index_high_column_name: {self.index_high_column_name}\n'
        f'action_update_scripts: {self.action_update_scripts}\n'
        f'action_test: {self.action_test}\n'
        '----------------------\n'
    )

    return_str += 'configured floodlights:\n'
    for floodlight in self.gtm_floodlight_list:
      return_str += str(floodlight) + '\n----------------------\n'

    for zone in self.zone_array:
      return_str += str(zone) + '\n----------------------\n'

    return return_str

  def print_dataframe(self, input_df: pd.DataFrame) -> None:
    """Converts a dataframe to a string and prints it to stdout.

    Args:
      input_df: any dataframe.

    Returns:
      None.
    """
    # Make sure indexes pair with number of rows.
    df = input_df.reset_index()

    if self.debug:
      print(df.to_string())

  # Function to automate data imports, data processing, mapping
  # and opportunity calculation.
  def read_sheets_data(self, zone: Bid2xGTMModel) -> pd.DataFrame:
    """Read sheet data for access to index info.

    Args:
      zone: the zone object.

    Returns:
      An updated dataframe now with a value_adjustment column of
      float numbers.
    """

    # Open associated spreadsheet.
    spreadsheet = self.sheet.gc.open_by_url(self.sheet.sheet_url)

    # Load the index data file tab for this zone.
    index_tab = spreadsheet.worksheet(zone.name)

    # Get all the values from the index data tab and convert into a Dataframe.
    index_data = index_tab.get_all_values()
    index_df = pd.DataFrame(index_data[1:], columns=index_data[0])

    if self.trace:
      print(f'Index DataFrame as read in from tab {zone.name}:')
      self.print_dataframe(index_df)

    return index_df

  def generate_multipliers_js(
      self, df: pd.DataFrame, value_column: str = 'Index', *dimensions: str
  ):
    """Generate a JavaScript string representing a nested multipliers object.

    Args:
        df (pd.DataFrame):  The input DataFrame.
        value_column (str): The name of the column containing the numeric
          values.
        *dimensions (str): Variable number of strings representing the columns
          to be used as dimensions for nesting the object.

    Returns:
        str: A JavaScript string defining the 'multipliers' object.
    """

    if not dimensions:
      raise ValueError('At least one dimension column must be provided.')

    multipliers = {}

    for _, row in df.iterrows():
      current_level = multipliers
      for i, dim in enumerate(dimensions):
        key = row[dim]
        if i < len(dimensions) - 1:
          if key not in current_level:
            current_level[key] = {}
          current_level = current_level[key]
        else:
          # Round to 9 decimal places for consistency
          current_level[key] = round(float(row[value_column]), 9)

    # Convert the Python dictionary to a JSON string, then format as JS
    js_multipliers_str = json.dumps(multipliers, indent=4)
    return f'  var multipliers = {js_multipliers_str};'

  def generate_get_multiplier_js_function(
      self, dimensions: Sequence[str]
  ) -> str:
    """Generate JavaScript string for the getMultiplier function.

    This version uses generic variable names (var1, var2, etc.) for the
    function parameters to avoid issues with dimension names containing
    special characters like hyphens, which are invalid in JS identifiers.

    Args:
      dimensions (list): A list of strings representing the dimension names.
                         The number of dimensions determines the number of
                         arguments for the generated function.

    Returns:
      str: A JavaScript string defining the 'getMultiplier' function.
    """
    if not dimensions:
      raise ValueError(
          'At least one dimension must be provided for the function.'
      )

    # Generate generic parameter names, e.g., ['var1', 'var2', ...]
    # These are guaranteed to be valid JavaScript identifiers.
    generic_params = [f'var{i+1}' for i in range(len(dimensions))]

    # Join the generic parameters for the function signature, e.g., "var1, var2"
    params_str = ', '.join(generic_params)

    # Build the nested lookup logic, mirroring the original's structure.
    # This creates a chain of checks to safely access nested properties.
    # e.g., ((multipliers && multipliers[var1]) &&
    #            (multipliers && multipliers[var1])[var2])
    final_lookup = 'multipliers'
    for param in generic_params:
      # The lookup now uses the safe, generic parameter name as the key.
      final_lookup = f'({final_lookup} && {final_lookup}[{param}])'

    # Append the fallback value to return if the lookup path is incomplete.
    final_lookup += ' || 1.0'

    # Construct the final JavaScript function string.
    js_function = f"""function getMultiplier({params_str}) {{
  return {final_lookup};
}}"""
    return js_function

  # Correct usage with reordered columns, if 'Index' is still the value.
  # You would need to explicitly tell the function which is the value column,
  # or ensure 'Index' is always the last.
  # For example, if you want 'Index' to be the
  # value column regardless of position:
  def generate_full_js_code_explicit(self, df, value_col_name='Index'):
    """Generates JavaScript string, explicitly identifying the value column.

    Args:
      df (pd.DataFrame): The input DataFrame.
      value_col_name (str): The name of the column containing the numeric
        values.

    Returns:
      str: The complete JavaScript string.
    """
    if value_col_name not in df.columns:
      raise ValueError(
          f"Value column '{value_col_name}' not found in DataFrame."
      )

    value_column = value_col_name
    dimensions = [col for col in df.columns if col != value_col_name]

    multipliers_js = self.generate_multipliers_js(df, value_column, *dimensions)
    get_multiplier_js = self.generate_get_multiplier_js_function(dimensions)

    return f'{multipliers_js}\n\n{get_multiplier_js}'

  def generate_js_function_call(
      self, dimensions: Sequence[str],
      example_values: Sequence[str] | None = None
  ) -> str:
    """Generates a JavaScript string that calls the getMultiplier function.

    Args:
        dimensions (list): A list of strings representing the dimension names
                            (e.g., ['region', 'model']).
        example_values (list, optional):  A list of actual values to use in
                                          the call.
                                          Must match the order of dimensions.
                                          If None, uses placeholder strings.

    Returns:
        str: A JavaScript string demonstrating the function call.
    """
    if not dimensions:
      return (
          '// No dimensions, so no meaningful call ',
          'to getMultiplier can be generated.'
      )

    call_args = []
    if example_values and len(example_values) == len(dimensions):
      for val in example_values:
        # Safely format string arguments with quotes, numbers as-is
        call_args.append(f"'{val}'" if isinstance(val, str) else str(val))
    else:
      # If no example_values or mismatch, use placeholders
      for dim in dimensions:
        call_args.append(f'{dim}')  # Placeholder string

    args_string = ', '.join(call_args)

    return f'conversion_value *= getMultiplier({args_string});'

  def replace_match(self, match: re.match, row_data: pd.Series) -> str:
    """Helper function to perform the replacement for each match.

    Args:
      match: A re match object.
      row_data: A pandas row object.

    Returns:
      The replaced string.
    """
    # Get the captured group (e.g., 'getRegion')
    column_name = match.group(1)
    if column_name in row_data:
      # Replace with the value from the current row
      return str(row_data[column_name])
    else:
      # If column not found, return the original
      # match (e.g., #getRegion#).
      return match.group(0)

  def write_javascript_function(self, input_df: pd.DataFrame) -> str:
    """Creates a string containing a JavaScript function for use in GTM.

    Args:
        input_df: dataframe from loading client supplied index file.

    Returns:
        A string representation of a JavaScript function for use
        with GTM to be loaded into a variable there.
    """

    # Walk the list of floodlights and see if any of them have a
    # 'per_row_condition' set to "lookup#...".  If so, set a
    # var called use_lookup to True which changes the format of
    # the output JavaScript
    use_lookup = False
    parts_after_first = []
    for floodlight_obj in self.gtm_floodlight_list:
      # if 'per_row_condition' in floodlight_obj:
      if hasattr(floodlight_obj, 'per_row_condition'):
        # Extract first part of 'per_row_condition' & check for
        # 'lookup' keyword.
        parts = floodlight_obj.per_row_condition.split('#')
        if parts[0] == 'lookup':
          use_lookup = True
          # If the keyword 'lookup' is first in a hash '#' delimited
          # list of strings then extract the part AFTER the 'lookup'
          # keyword and keep the list of strings as they are used
          # for the calling of the lookup function.  For example,
          # 'lookup#region#{{getCarModel}}' would use 'region'
          # and {{getCarModel}} in the list of variables for the
          # constructed lookup function and table.
          parts_after_first = parts[1:]

    # Set the header part of the function for GTM.
    js_function_string_start = []
    js_function_string_start.append('function() {\n')
    js_function_string_start.append('  var conversion_value = 0.0;\n')
    js_function_string_start.append(self.gtm_preprocessing_script + '\n')

    if use_lookup:
      js_output_explicit = self.generate_full_js_code_explicit(
          input_df, value_col_name='Index'
      )
      js_function_string_start.append('\n')
      js_function_string_start.append(js_output_explicit)
      js_function_string_start.append('\n')

    fl_iter = 0

    # Run a loop for the list of floodlight names passed.
    for floodlight_obj in self.gtm_floodlight_list:

      # Determine clause prefix.
      if fl_iter > 0:
        fl_clause_prefix = 'else '
      else:
        fl_clause_prefix = ''

      # The dictionary for the gtm_floodlight_list contains a
      # 'floodlight_name', 'per_row_condition', 'total_var', and
      # optionally a 'floodlight_condition'.
      # If floodlight_condition exists then use it as the conditional statement
      # to identify a specific floodlight in the JavaScript fn being generated.
      # If it doesn't exist then assume the name of the {{Event}} will be the
      # same as the given name of the floodlight.
      if hasattr(floodlight_obj, 'floodlight_condition'):
        conditional = floodlight_obj.floodlight_condition
      else:
        floodlight_name = floodlight_obj.floodlight_name
        conditional = ' {{Event}} == ' + f'"{floodlight_name}" '

      js_function_string_start.append(f'  {fl_clause_prefix}')
      js_function_string_start.append(f'if ( {conditional} ) ')
      js_function_string_start.append('{\n')
      # Once inside the conditional the very first thing is to assign
      # conversion_value to the configured total_var.  This ensures
      # we have a default value for the conversion even if none of the
      # 'per_row_condition' statements fail to match.
      js_function_string_start.append('    conversion_value = parseFloat(')
      js_function_string_start.append('{{')
      # The default action is to use the total_var as a GTM varaiable to
      # evaluate in the JavaScript.  If it is not provided then use the
      # floodlight name.
      if hasattr(floodlight_obj, 'total_var'):
        js_function_string_start.append(f'{floodlight_obj.total_var}')
      else:
        js_function_string_start.append(f'{floodlight_obj.floodlight_name}')
      js_function_string_start.append('}});\n')

      # Advance the floodlight counter.
      fl_iter = fl_iter + 1

      # Create the repeating part of the function string by
      # starting with a blank list.
      js_function_string_middle = []

      # If NOT using a lookup table then use the 'per_row_condition' as
      # the mechanism by which to write the innder conditional.
      if not use_lookup:
        # Extract variables to be used from 'per_row_condition' line.
        replacement_pattern = re.compile(r'#([^#]+)#')

        for _, row_data in input_df.iterrows():
          # Create a partial function with row_data "frozen"
          replace_match_partial = partial(self.replace_match, row_data=row_data)
          if hasattr(floodlight_obj, 'per_row_condition'):
            substituted_condition = replacement_pattern.sub(
                replace_match_partial, floodlight_obj.per_row_condition
            )
          else:
            print(
                'per_row_condition key not defined for this ', 'floodlight: ',
                floodlight_obj, ' cannot continue.'
            )
            exit(-2)

          # Define the column being referenced for adjustments to
          # the conversion value.
          adjustment = row_data[self.value_adjustment_column_name]

          js_function_string_middle.append('    if (')
          js_function_string_middle.append(substituted_condition)
          js_function_string_middle.append(' ) {\n')
          js_function_string_middle.append('      conversion_value *= ')
          # This is the index adjustment/multiplier
          # to the default conv. value.
          js_function_string_middle.append(f'{adjustment}; ')
          js_function_string_middle.append('  }\n')

      # Last statement in floodlight loop - append all from this iteration
      # of the loop to the start start list.
      js_function_string_start.append(''.join(js_function_string_middle))
      js_function_string_start.append('  }\n')

    # Define the end of the JavaScript function.
    if use_lookup:
      js_call = self.generate_js_function_call(parts_after_first)
      js_function_string_end = '  ' + js_call
    else:
      js_function_string_end = ''

    js_function_string_end += self.gtm_postprocessing_script + '\n'
    js_function_string_end += '  return conversion_value;\n}'

    # Assemble the JavaScript function - join the start to the end
    js_function_string = ''.join(js_function_string_start)
    js_function_string += js_function_string_end

    # Return the finalized JavaScript function for use in GTM.
    return js_function_string

  # Update the variable using GTM API.
  def update_gtm_variable(
      self, service: Any, new_function: str, zone: Bid2xGTMModel
  ) -> bool:
    """Update Google Tag Manager variable with new JavaScript function.

    Args:
        service: a service object previously opened with the GTM API.
        new_function: a string containing the value to update within the
          variable_id.
        zone: the zone object.

    Returns:
        The function returns True upon successful update or False if
        it was unable to update the variable.
    """
    # Create a new workspace version to operate on.
    prod_workspace_path = (
        f'accounts/{zone.account_id}/containers/{zone.container_id}'
    )

    now = datetime.datetime.now()
    datetime_string = now.strftime('%d/%m/%Y %H:%M:%S')
    datetime_string_simplified = now.strftime('%Y%m%d%H%M%S')

    gtm_body_name = f'Copy of production {datetime_string_simplified}'
    gtm_body_notes = (
        f'Auto-generated workspace - made in GTM API - {datetime_string}'
    )
    gtm_new_workspace_body = {'name': gtm_body_name, 'notes': gtm_body_notes}

    if self.trace:
      print(f'gtm_new_workspace_body: {gtm_new_workspace_body}')
      print(f'prod_workspace_path: {prod_workspace_path}')

    gtm_new_workspace = (
        service.accounts().containers().workspaces().create(
            parent=prod_workspace_path, body=gtm_new_workspace_body
        ).execute()
    )

    # Return value of call to create new workspace gives new ids - assign
    # these values.
    if gtm_new_workspace and gtm_new_workspace['fingerprint']:
      account_id = gtm_new_workspace['accountId']
      container_id = gtm_new_workspace['containerId']
      workspace_id = gtm_new_workspace['workspaceId']
      if self.trace:
        print(f'gtm_new_workspace return value: {gtm_new_workspace}')
    else:
      return False

    # Build the path for getting / updating the variable
    # using the passed args.
    var_req = (
        f'accounts/{account_id}/containers/{container_id}/'
        f'workspaces/{workspace_id}/variables/{zone.variable_id}'
    )

    # Get the current value of the variable in GTM.
    gtm_var = (
        service.accounts().containers().workspaces().variables().get(
            path=var_req
        ).execute()
    )

    if self.trace:
      print(f'GTM var is: {gtm_var}')
      print(f'Current internal function is{gtm_var["parameter"][0]["value"]}')

    # Set gtm_var holder to have new value of function that was passed.
    gtm_var['parameter'][0]['value'] = new_function

    if self.trace:
      print(f'GTM var after update is: {gtm_var}')
      print(f'Proposed internal function is{gtm_var["parameter"][0]["value"]}')

    # Update GTM with the new version of gtm_var that has been updated
    # with the new JavaScript function.
    gtm_updated = (
        service.accounts().containers().workspaces().variables().update(
            path=var_req, body=gtm_var
        ).execute()
    )

    if self.trace:
      print(f'return value from update on GTM is: {gtm_updated}')

    # Check to see if the value returned for the variable's value is the
    # same as what it was passed.  This indicates a successful update.
    if gtm_updated['parameter'][0]['value'] == gtm_var['parameter'][0]['value']:
      if self.trace:
        print('Update variable success')

    else:
      # Not a good return value, return from function.
      return False

    # Prep for versioned workspace.
    gtm_path = (
        f'accounts/{account_id}/containers/{container_id}/'
        f'workspaces/{workspace_id}'
    )
    gtm_name = f'Auto-versioned container {datetime_string_simplified}'
    gtm_notes = (
        f'This container auto-versioned on {datetime_string} using GTM API'
    )
    gtm_versioned_workspace_body = {'name': gtm_name, 'notes': gtm_notes}

    if self.trace:
      print('Create_version()... ')
      print(f'gtm_path = {gtm_path}')
      print(f'gtm_versioned_workspace_body = {gtm_versioned_workspace_body}')

    # Created versioned workspace.
    gtm_versioned_workspace = (
        service.accounts().containers().workspaces().create_version(
            path=gtm_path, body=gtm_versioned_workspace_body
        ).execute()
    )

    if gtm_versioned_workspace:
      # Get version ID here and save to variable for use with publish.
      version_id = gtm_versioned_workspace['containerVersion'][
          'containerVersionId']

      if self.trace:
        print(f'gtm_versioned_workspace: {gtm_versioned_workspace}')
        print('new version success')
    else:
      return False

    # Prep for publish command.
    gtm_publish_path = (
        f'accounts/{account_id}/containers/{container_id}/versions/{version_id}'
    )
    gtm_published = (
        service.accounts().containers().versions().publish(
            path=gtm_publish_path,
        ).execute()
    )

    # Check return value of gtm_publish_path.
    if gtm_published:
      if self.debug:
        print(f'GTM variable: {var_req} successfully published.')
    else:
      return False

    return True

  # Starts the data reading and custom bidding process.
  def process_script(
      self,
      service: Any,
      zone_array: list[Bid2xGTMModel],
      test_flag: bool = False  # By default it's not a test.
  ) -> bool:
    """Orchestrates the variable change in GTM.

    Args:
      service: A service object previously opened with the GTM API.
      zone_array: A list of Bid2xGTMModel objects to walk and publish.
      test_flag: Boolean that determine whether this is a test.  A test
            does not write to GTM but goes through the other actions.

    Returns:
      True if process is a success.  False otherwise.
    """

    for zone in zone_array:
      # Read the index data from a spreadsheet into a Dataframe.
      index_df = self.read_sheets_data(zone)
      js_function = self.write_javascript_function(index_df)

      # Write the new function out to the test column in the associated
      # Google Sheet in the tab 'JS_Scripts' (by default).
      self.sheet.update_status_tab(
          bid2x_var.GTM_STATUS_TAB, zone, js_function, test_run=test_flag
      )

      if self.debug:
        print('Generated JS function returned:')
        print(js_function)

      # If there's a good service and a good function and this
      # is NOT a test then update the GTM variable.
      if service and js_function and not test_flag:
        ret_val = self.update_gtm_variable(service, js_function, zone)

        if ret_val:
          print(
              f'Success updating zone {zone.name} GTM variable to new',
              f'value of:{chr(10)}{js_function}',
          )
        else:
          print('Error updating GTM variable with function.')
          continue  # Process next loop.
      else:
        print('No GTM service, no valid function, or this is a test.')
        continue  # Process next loop.

    return True

  def top_level_copy(self, source: Any) -> None:
    """Copy all config file GTM settings to this object.

    Args:
      source: The config file opened and decoded into readable format.

    Returns:
      None.
    """
    attributes_to_copy = [
        'debug',
        'trace',
        'gtm_preprocessing_script',
        'gtm_postprocessing_script',
        'value_adjustment_column_name',
        'index_low_column_name',
        'index_high_column_name',
        'action_update_scripts',
        'action_test',
        'zones_to_process',
    ]

    for attr in attributes_to_copy:
      if attr in source:
        setattr(self, attr, source[attr])

    self.gtm_floodlight_list = [
        GTMFloodlight(**item) for item in source['gtm_floodlight_list']
    ]

    return
