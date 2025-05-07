"""BidToX - bid2x_spreadsheet application module.

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

  This module contains the bid2x_spreadsheet class which is used to
  read and write to a Google spreadsheet.  The class contains methods
  to read and write to the spreadsheet and to create new tabs within
  the spreadsheet.  It also contains methods to read and write to
  specific columns within the spreadsheet.
"""

import datetime
import time
from typing import Any, List

from bid2x_util import is_recoverable_http_error
import bid2x_var
from google.api_core import exceptions
from googleapiclient import errors
import gspread

HttpError = errors.HttpError
GoogleAPICallError = exceptions.GoogleAPICallError


class Bid2xSpreadsheet:
  """Spreadsheet class for the bid2x application.

  Attributes:
      sheet_url: The URL of the spreadsheet.
      sheet_id: The ID of the spreadsheet.
      sheets_service: The service object for the Google Sheets API.
      json_auth_file: The path to the JSON authentication file.
      _platform_type: The platform type of the script.
      column_status: The column name for the status column.
      column_lineitem_id: The column name for the line item ID column.
      column_lineitem_name: The column name for the line item name column.
      column_lineitem_type: The column name for the line item type column.
      column_campaign_id: The column name for the campaign ID column.
      column_advertiser_id: The column name for the advertiser ID column.
      column_custom_bidding: The column name for the custom bidding column.
      debug: The debug flag.
      trace: The trace flag.
      clear_onoff: The clear on/off flag.
      gc: The gspread object.
      COLUMN_OFFSET: The column offset.
      MAX_RETRIES: The maximum number of retries.

  Methods:
      read_dv_line_items(self, service, line_item_name_pattern,
      zone_array, defer_pattern): Reads DV360 line items and
      populates the associated spreadsheet's tabs with information
      from client's account structure in DV.
      get_affected_line_items_from_sheet(self, zone_string): Gets
      the data from a single tab within the linked spreadsheet and
      returns all rows where the spreadsheet is marked 'Yes' to
      generate the custom bidding script for that Line Item.
      get_line_item_data_from_sheet(self, zone_string): Gets the
      data from a single tab within the linked spreadsheet and
      returns all rows where the spreadsheet is marked 'Yes' to
      generate the custom bidding script for that Line Item.
      get_line_item_data_from_sheet(self, zone_string): Gets the
      data from a single tab within the linked spreadsheet and
      returns all rows where the spreadsheet is marked 'Yes' to
      generate the custom bidding script for that Line Item.
      get_line_item_data_from_sheet(
  """

  sheet_url: str
  sheet_id: int
  sheets_service = None
  json_auth_file: str
  _platform_type: str
  column_status: str
  column_lineitem_id: str
  column_lineitem_name: str
  column_lineitem_type: str
  column_campaign_id: str
  column_advertiser_id: str
  column_custom_bidding: str
  debug: bool
  trace: bool
  clear_onoff: bool
  gc: gspread
  COLUMN_OFFSET = 64  # Add to column # to get actual column letter.
  MAX_RETRIES = 5  # Number of retries when API calls fail

  def __init__(self, sheet_id: str, auth_filename: str):
    self.sheet_id = sheet_id
    self.sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
    self.json_auth_file = auth_filename
    self.sheets_service = None
    self._platform_type = bid2x_var.PlatformType.GTM
    self.column_status = 'A'
    self.column_lineitem_id = 'B'
    self.column_lineitem_name = 'C'
    self.column_lineitem_type = 'D'
    self.column_campaign_id = 'E'
    self.column_advertiser_id = 'F'
    self.column_custom_bidding = 'K'
    self.debug = False
    self.trace = False
    self.clear_onoff = True
    self.gc = gspread.service_account(filename=auth_filename)

  def __str__(self) -> str:
    """Override str method to return a sensible string.

    Args:
        None.
    Returns:
        A formatted string containing a formatted list of object properties.
    """

    return_str = (
        f'sheet_id: {self.sheet_id}\n'
        f'sheet_url: {self.sheet_url}\n'
        f'json_auth_file: {self.json_auth_file}\n'
        f'gc (link to sheet): {self.gc}\n'
        f'debug: {self.debug}\n'
        f'trace: {self.trace}\n'
    )

    if self._platform_type == bid2x_var.PlatformType.DV.value:
      return_str = (
          return_str + f'column_status: {self.column_status}\n'
          f'column_lineitem_id: {self.column_lineitem_id}\n'
          f'column_lineitem_name: {self.column_lineitem_name}\n'
          f'column_lineitem_type: {self.column_lineitem_type}\n'
          f'column_campaign_id: {self.column_campaign_id}\n'
          f'column_advertising: {self.column_advertiser_id}\n'
          f'column_custom_bidding:{self.column_custom_bidding}\n'
          f'clear_onoff: {self.clear_onoff}'
      )
    elif self._platform_type == bid2x_var.PlatformType.GTM.value:
      return_str += 'GTM spreadsheet specifics'

    return return_str

  def __getstate__(self):
    state = self.__dict__.copy()  # Start with all attributes.
    del state['gc']  # Remove the gc attribute.
    del state['sheets_service']  # Remove the sheets_service attribute.
    return state  # Return the modified state dictionary.

  def read_dv_line_items(
      self,
      service: Any,
      line_item_name_pattern: str,
      zone_array: Any,  # Should be a List[bid2x_model].
      defer_pattern: bool,
  ) -> bool:
    """Read DV360 line items and populate the spreadsheet tabs.

    Args:
        service: DV360 connection object
        line_item_name_pattern: A string containing a pattern to match in line
          item names.  Those line items with names containing substrings with
          this value will be by default turned 'on' in the spreadsheet
          and for use with this system.
        zone_array: array of bid2x_model objects describing all the
            zones or campaigns that are in use.
        defer_pattern: A Boolean that, when true, does not use the
            line_item_name_pattern string variable to match against line item
            name substrings but rather leaves the on/off status of the line
            items listed as untouched.

    Returns:
      Returns True if able to get to the end of the function, other it
      returns False if it had to exit for any reason along the way.

    Discussion:
      This method is _ridiculously_ long and should be broken up.  The portions
      that deal with getting data from DV should be moved to within bid2x_dv.py
      and the portions dealing with the spreadsheet should stay here but
      be simplified into several methods.  One thing that makes this method
      too long is the error handling.  Need to investigate whether some generic
      error handling or an error handling framework for LIKE calls (i.e. DV
      vs. gspread) can be created to make the logic here easier to follow.
    """

    # Connect to Sheets.
    spreadsheet_id = self.sheet_id

    # We require a valid zone_array and a valid spreadsheet to continue,
    # if either are missing then return from this method.
    if not zone_array or not spreadsheet_id:
      # As per GoB Gerrit CL 131576:
      # Change all prints to logging calls to permit centralized control.
      print('Missing zone_array or spreadsheet_id. Exiting.')
      return False

    # Walk the array of bid2x_model objects and do
    # lookups in DV360 to gather line items.
    for zone in zone_array:

      if self.debug:
        print(f'Current zone object is: {zone.name}')

      # Clear the sheet in the range A2:F1000.
      self.clear_sheet(zone.name)

      # Generate the string to filter this query by.
      filter_string = f'campaignId={zone.campaign_id}'

      # Ask DV360 for a list of line items for this advertiser where
      # the campaignId = the value for this loop.

      all_line_items_for_zone = []
      next_page_token = None

      # Section 1 - Get matching DV line items from DV360 API.

      print(
          f'Fetching line items for Advertiser ID: {zone.advertiser_id}, ',
          f'Campaign ID: {zone.campaign_id}',
      )
      page_num = 1
      # As per GoB Gerrit CL 131576:
      # Fast-follow to add unit tests here to ensure multiple nested loops
      # behave as expected.
      while True:  # Loop for paging through line item requests/responses.
        retry_count = 0
        delay = bid2x_var.HTTP_RETRY_TIMEOUT
        current_page_response = None
        while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
          try:
            if self.debug:
              print(
                  f'Requesting page {page_num} for advertiser ',
                  f'{zone.advertiser_id} with page token: {next_page_token}',
              )

            # Use LARGE_PAGE_SIZE to speed up transfers.
            request_line_items = (
                service.advertisers()
                .lineItems()
                .list(
                    advertiserId=f'{zone.advertiser_id}',
                    pageSize=bid2x_var.LARGE_PAGE_SIZE,
                    filter=filter_string,
                    pageToken=next_page_token,
                )
            )
            current_page_response = request_line_items.execute()
            break  # Success, exit retry loop.

          except HttpError as e:
            print(
                f'HttpError with DV360 listing line items (page {page_num}) '
                f'for advertiser {zone.advertiser_id}: {e}'
            )
            if is_recoverable_http_error(e.resp.status):
              print(f'Retrying in {delay} seconds...')
              time.sleep(delay)
              retry_count += 1
              delay *= 2
              if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
                print(
                    'Failed to list line items after ',
                    f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.',
                )
                raise
            else:
              raise  # Non-recoverable HTTP error.
          except GoogleAPICallError as e:  # More specific Google API errors.
            print(
                f'Google API error while listing line items (page {page_num}) '
                f'for advertiser {zone.advertiser_id}: {e}'
            )
            raise
          except TimeoutError:
            print(
                f'Request timed out listing line items (page {page_num}) for '
                f'advertiser {zone.advertiser_id}. Please check your network.'
            )
            # Depending on policy, you might want to retry timeouts too
            # For now, re-raising as per original code.
            raise
          except Exception as e:  # Catch any other unexpected errors.
            print(
                'An unexpected error occurred while fetching line items ',
                f'(page {page_num}) for advertiser {zone.advertiser_id}: {e}',
            )
            raise

        # Download of page of line items is complete.  Process it.
        if current_page_response and 'lineItems' in current_page_response:
          all_line_items_for_zone.extend(current_page_response['lineItems'])
          if self.debug:
            print(
                f'Fetched {len(current_page_response["lineItems"])} items on',
                f' page {page_num}. Total fetched so far for this zone:',
                f'{len(all_line_items_for_zone)}',
            )
        else:
          if self.debug:
            print(
                f'No lineItems field in response for page {page_num} ',
                'or empty response.',
            )
          # This might happen if the last page was full and the next page
          # token pointed to an empty page or if there were no items at all.

        next_page_token = current_page_response.get('nextPageToken')
        if not next_page_token:
          if self.debug:
            print(
                'No nextPageToken found. Finished fetching all ',
                f'{len(all_line_items_for_zone)} line items for ',
                f'advertiser {zone.advertiser_id}.',
            )
          break  # Exit pagination loop.
        page_num += 1

      if not all_line_items_for_zone:
        if self.debug:
          print(
              'No line items found or fetched for zone ',
              f'{zone.name} after attempting pagination.',
          )
      else:
        if self.debug:
          print(
              f'Processing a total of {len(all_line_items_for_zone)} ',
              f'line items for zone {zone.name}.',
          )

      # Section 2:  Walk results and prep an array for Google Sheets update.

      line_items_data_for_sheet: List[List[Any]] = []
      auto_ons_data_for_sheet: List[List[str]] = []

      for line_item in all_line_items_for_zone:
        # Generate the rows of line item data for transfer to Google
        # Sheets except do not allow line item types that are YouTube
        # related.
        if (
            line_item.get('lineItemType')
            not in (
                'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_NON_SKIPPABLE',
                'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_REACH',
                'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_ACTION',
            )
            # Note here for terwilleger@google.com:
            # as discussed, an empty string ('') is still 'in' the displayName.
            and line_item_name_pattern in line_item['displayName']
        ):

          line_items_data_for_sheet.append(
              [
                  line_item.get('entityStatus'),
                  line_item.get('lineItemId'),
                  line_item.get('displayName'),
                  line_item.get('lineItemType'),
                  line_item.get('campaignId'),
                  line_item.get('advertiserId'),
              ]
          )

          # Build array for optional auto_on.
          if line_item_name_pattern in line_item.get('displayName'):
            auto_ons_data_for_sheet.append(['Yes'])
          else:
            auto_ons_data_for_sheet.append(['No'])

      # Section 3 - Connect to spreadsheet to the tab representing the
      #             current zone.

      retry_count = 0
      delay = bid2x_var.HTTP_RETRY_TIMEOUT
      current_tab = None

      while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
        # Spreadsheet tab name should be the name of the bid2x_model.
        # item (.name).
        try:
          current_tab = self.gc.open_by_key(spreadsheet_id).worksheet(zone.name)
          break  # Success, exit retry loop.
        except gspread.exceptions.SpreadsheetNotFound:
          print(
              f'Error with gspread: Spreadsheet with ID '
              f'{spreadsheet_id} not found.'
          )
          raise  # Reraise the exception for higher-level handling.
        except gspread.exceptions.WorksheetNotFound:
          print(
              f'Error with gspread: Worksheet "{zone.name}" ',
              'not found in the spreadsheet.',
          )
          raise  # Reraise the exception.
        except gspread.exceptions.APIError as e:
          print(
              'Error with gspread while connecting to tab '
              f'"{zone.name}": {e}'
          )
          raise  # Reraise the exception.
        except TimeoutError:
          print(
              'Request timed out while connecting to tab ',
              f'"{zone.name}".  Please check your network ',
              'connection.',
          )
          raise  # Reraise the exception.
        except gspread.exceptions.GSpreadException as e:
          print(
              f'An unexpected gspread error occurred while '
              f'connecting to tab "{zone.name}": {e}'
          )
          raise  # Reraise the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            print(f'Retrying in {delay} seconds...')
            time.sleep(delay)
            retry_count += 1
            delay *= 2

            # If we get here, we've exceeded the maximum retries.
            if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
              print(
                  'Failed to opening worksheet after ',
                  f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.',
              )
              raise
          else:
            raise

      # Section 4 - Update the data in the current tab.

      retry_count = 0
      delay = bid2x_var.HTTP_RETRY_TIMEOUT

      while (
          retry_count < Bid2xSpreadsheet.MAX_RETRIES and current_tab is not None
      ):
        try:
          # Update starting from A2 (row 2).
          current_tab.update(
              values=line_items_data_for_sheet,
              range_name=f'{self.column_status}2',
          )
          break  # Success, exit retry loop.
        except gspread.exceptions.APIError as e:
          print(
              'Error communicating with Google Sheets API while ',
              f'updating tab f{zone.name}:{e}',
          )
          raise  # Reraises the exception.
        except TimeoutError:
          print(
              f'Request timed out while updating tab f{zone.name}. ',
              'Please check your network connection.',
          )
          raise  # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(f'Error with gspread while updating tab f{zone.name}:{e}')
          raise  # Reraises the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            print(f'Retrying in {delay} seconds...')
            time.sleep(delay)
            retry_count += 1
            delay *= 2

            # If we get here, we've exceeded the maximum retries.
            if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
              print(
                  'Failed to updating tab after '
                  f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
              )
              raise
          else:
            raise

      # Section 5 - Optionally auto-enable line items matching pattern.

      if not defer_pattern and current_tab is not None:
        retry_count = 0
        delay = bid2x_var.HTTP_RETRY_TIMEOUT

        try:
          # Update starting from K2 (row 2).
          current_tab.update(
              values=auto_ons_data_for_sheet,
              range_name=f'{self.column_custom_bidding}2',
          )
        except gspread.exceptions.APIError as e:
          print(
              'Error with gspread while updating range ',
              f'{self.column_custom_bidding}2: {e}',
          )
          raise  # Reraises the exception.
        except TimeoutError:
          print(
              'Request timed out while updating range ',
              f'{self.column_custom_bidding}2. ',
              'Please check your network connection.',
          )
          raise  # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(
              'An unexpected gspread error occurred while updating ',
              f'range {self.column_custom_bidding}2: {e}',
          )
          raise  # Reraises the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            print(f'Retrying in {delay} seconds...')
            time.sleep(delay)
            retry_count += 1
            delay *= 2

            # If we get here, we've exceeded the maximum retries.
            if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
              print(
                  'Failed to updating range after '
                  f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
              )
              raise
          else:
            raise

    return True

  def get_affected_line_items_from_sheet(self, zone_string: str) -> list[int]:
    """Returns all rows in spreadsheet marked 'Yes'.

    Args:
      zone_string: a string corresponding to the label on a tab in the
        Google sheet.

    Returns:
      A list of line items that need to be included in the custom bidding.
    """
    # Get reference to already connected Sheets.
    spreadsheet_id = self.sheet_id
    # Open the spreadsheet tab name that is the passed zone string.

    retry_count = 0
    delay = bid2x_var.HTTP_RETRY_TIMEOUT

    current_tab: gspread.models.Worksheet = None

    while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
      try:
        current_tab = self.gc.open_by_key(spreadsheet_id).worksheet(zone_string)
        break
      except gspread.exceptions.SpreadsheetNotFound:
        print(
            'Error with gspread: Spreadsheet with ',
            f'ID {spreadsheet_id} not found.',
        )
        raise  # Reraise the exception for higher-level handling
      except gspread.exceptions.WorksheetNotFound:
        print(
            f'Error with gspread: Worksheet "{zone_string}" not ',
            'found in the spreadsheet.',
        )
        raise  # Reraise the exception
      except gspread.exceptions.APIError as e:
        print(
            'Error with gspread while connecting to ',
            f'tab "{zone_string}": {e}',
        )
        raise  # Reraise the exception
      except TimeoutError:
        print(
            f'Request timed out while connecting to tab "{zone_string}". ',
            'Please check your network connection.',
        )
        raise  # Reraise the exception
      except gspread.exceptions.GSpreadException as e:
        print(
            'An unexpected gspread error occurred while ',
            f'connecting to tab "{zone_string}": {e}',
        )
        raise  # Reraise the exception
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          print(f'Retrying in {delay} seconds...')
          time.sleep(delay)
          retry_count += 1
          delay *= 2

          # If we get here, we've exceeded the maximum retries
          if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
            print(
                f'Failed to get all records after '
                f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
            )
            raise
        else:
          raise

      if current_tab is None:
        print('current_tab is None - cannot proceed')
        return []

    if type(current_tab).__name__ != 'Worksheet':
      print('current_tab is not a gspread.models.Worksheet - cannot proceed')
      return []

    list_of_dicts = None
    retry_count = 0
    delay = bid2x_var.HTTP_RETRY_TIMEOUT

    while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
      # Get list of all records on the opened spreadsheet.
      try:
        list_of_dicts = current_tab.get_all_records()
        break  # Success, exit retry loop.
      except gspread.exceptions.GSpreadException as e:
        print(
            'An unexpected gspread error occurred during ',
            f'get_all_records() call: {e}',
        )
        raise  # Reraise the exception for higher-level handling
      except ValueError as e:
        print(
            'Error with gspread during get_all_records() call. ',
            f'Data might be improperly formatted: {e}',
        )
        raise  # Reraise the exception
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          print(f'Retrying in {delay} seconds...')
          time.sleep(delay)
          retry_count += 1
          delay *= 2

          # If we get here, we've exceeded the maximum retries
          if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
            print(
                f'Failed to get all records after '
                f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
            )
            raise
        else:
          raise

    if current_tab is None or list_of_dicts is None:
      print('current_tab is None - cannot proceed')
      return []

    # Create an empty list of processed line items.
    # Some Line Items may be disabled, we are building a list of line item
    # IDs that are enabled for the custom bidding to pass back.
    processed_line_items = []
    for row in list_of_dicts:
      # Change these static texts to variables.  For now the
      # spreadsheet columns are bound to these names.
      if row['Generate Custom Bidding'].lower() == 'yes':
        if processed_line_items.count(row['Line Item ID']) == 0:
          processed_line_items.append(row['Line Item ID'])

    return processed_line_items

  def clear_sheet(self, zone_string: str) -> bool:
    """Clear specific cells in the passed tab name.

    Args:
      zone_string: a string corresponding to the label on a tab in the
        Google sheet.

    Returns:
        True if able to complete the function successfully.
    """
    # Get reference to already connected Sheets.
    spreadsheet_id = self.sheet_id

    retry_count = 0
    delay = bid2x_var.HTTP_RETRY_TIMEOUT
    current_tab: gspread.models.Worksheet = None

    while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
      try:
        # Spreadsheet tab name is the name of the bid2Model iteam (.name).
        current_tab = self.gc.open_by_key(spreadsheet_id).worksheet(zone_string)
        break  # Success, exit retry loop.
      except gspread.exceptions.SpreadsheetNotFound:
        print(
            'Error with gspread: Spreadsheet with ',
            f'ID {spreadsheet_id} not found.',
        )
        raise  # Reraises the exception.
      except gspread.exceptions.WorksheetNotFound:
        print(
            f'Error with gspread: Worksheet "{zone_string}" ',
            'not found in the spreadsheet.',
        )
        raise  # Reraises the exception.
      except gspread.exceptions.APIError as e:
        print(
            'Error with gspread while connecting to tab '
            f'"{zone_string}": {e}'
        )
        raise  # Reraises the exception.
      except TimeoutError:
        print(
            f'Request timed out while connecting to tab "{zone_string}"',
            '. Please check your network connection.',
        )
        raise  # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(
            'An unexpected gspread error occurred while ',
            f'connecting to tab "{zone_string}": {e}',
        )
        raise  # Reraises the exception.
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          print(f'Retrying in {delay} seconds...')
          time.sleep(delay)
          retry_count += 1
          delay *= 2

          # If we get here, we've exceeded the maximum retries
          if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
            print(
                'Failed to open worksheet after '
                f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
            )
            raise
        else:
          raise

    # Build the address string containing the range used
    # to 'clear' the spreadsheet
    clear_string = f'{self.column_status}'
    clear_string += f'{bid2x_var.SPREADSHEET_FIRST_DATA_ROW}'
    clear_string += ':'
    clear_string += f'{self.column_advertiser_id}'
    clear_string += f'{bid2x_var.SPREADSHEET_LAST_DATA_ROW}'

    retry_count = 0
    delay = bid2x_var.HTTP_RETRY_TIMEOUT

    while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
      # Perform batch clear operation.
      try:
        current_tab.batch_clear([clear_string])
        break  # Success, exit retry loop.
      except gspread.exceptions.APIError as e:
        print(
            'Error with gspread during batch_clear operation ',
            f'on tab "{zone_string}": {e}',
        )
        raise  # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(
            'An unexpected gspread error occurred during batch_clear ',
            f'on tab "{zone_string}": {e}',
        )
        raise  # Reraises the exception.
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          print(f'Retrying in {delay} seconds...')
          time.sleep(delay)
          retry_count += 1
          delay *= 2

          # If we get here, we've exceeded the maximum retries
          if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
            print(
                'Failed batch clear operation after '
                f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
            )
            raise
        else:
          raise

    # Build array of 'No' values for column in spreadsheet to
    # clear out the custom bidding 'Yes' selections.
    if self.clear_onoff:
      on_off_array = [['No']] * (
          bid2x_var.SPREADSHEET_LAST_DATA_ROW
          - bid2x_var.SPREADSHEET_FIRST_DATA_ROW
      )

      retry_count = 0
      delay = bid2x_var.HTTP_RETRY_TIMEOUT

      while retry_count < Bid2xSpreadsheet.MAX_RETRIES:
        try:
          current_tab.update(
              values=on_off_array, range_name=f'{self.column_custom_bidding}2'
          )
          break  # Success, exit retry loop.
        except gspread.exceptions.APIError as e:
          print(
              'Error with gspread during update of ',
              f'range {self.column_custom_bidding}',
              f'{bid2x_var.SPREADSHEET_FIRST_DATA_ROW} on',
              f'tab "{zone_string}": {e}',
          )
          raise  # Reraises the exception.
        except gspread.exceptions.GSpreadException as e:
          print(
              'An unexpected gspread error occurred during update ',
              f'on tab "{zone_string}": {e}',
          )
          raise  # Reraises the exception.
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            print(f'Retrying in {delay} seconds...')
            time.sleep(delay)
            retry_count += 1
            delay *= 2

            # If we get here, we've exceeded the maximum retries
            if retry_count == Bid2xSpreadsheet.MAX_RETRIES:
              print(
                  'Failed batch clear operation after '
                  f'{Bid2xSpreadsheet.MAX_RETRIES} attempts.'
              )
              raise
          else:
            raise

    return True

  def update_status_tab(
      self,
      status_tab_name: str,
      zone: Any,
      cust_bidding_function_string: str,
      test_run: bool,
  ) -> bool:
    """Method to update_status_tab.

    Args:
      status_tab_name: The name of the Sheets tab on which to write the
            status update.
      zone: A bid2x_model object containing (most importantly for this method)
            the rows and columns within the status tab to update.
      cust_bidding_function_string: The string that was generated for the
                                    update or test.
      test_run: A Boolean indicating that the call is for a test when True.
                Otherwise it is assumed that the call is being made in
                conjunction with an update to the actual script.
    Returns:
      True on successful completion of the function.
    """
    # Update status tab.
    # Spreadsheet tab name should match key in dict.

    try:
      cbscripts_sheet = self.gc.open_by_key(self.sheet_id).worksheet(
          status_tab_name
      )
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Error: Spreadsheet not found for worksheet {status_tab_name}')
      raise  # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound as e:
      print(f'Error connecting to worksheet CB_Scripts: {e}')
      raise  # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print(
          'Error communicating with Google Sheets API for ',
          f'worksheet CB_Scripts: {e}',
      )
      raise  # Reraises the exception.
    except TimeoutError:
      print('Request timed out. Please check your network connection.')
      raise  # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected error occurred: {e}')
      raise  # Reraises the exception.

    # Work out the row and column for this update.
    if not test_run:
      update_row = zone.update_row
      update_col = chr(Bid2xSpreadsheet.COLUMN_OFFSET + zone.update_col)
    else:
      update_row = zone.test_row
      update_col = chr(Bid2xSpreadsheet.COLUMN_OFFSET + zone.test_col)

    # Write the most recent custom bidding function to the right
    # place on the CB_Scripts tab.
    if update_row:
      current_datetime = datetime.datetime.now()
      try:
        cbscripts_sheet.update(
            values=[[cust_bidding_function_string, f'{current_datetime}']],
            range_name=f'{update_col}{update_row}',
        )
      except Exception as e:
        print(f'Error updating test run into worksheet: {e}')
        raise  # Reraises the exception.

    return True

  def top_level_copy(self, source: Any, platform_type: str) -> None:
    """Method to make a copy of top-level parameters within the source.

    Args:
      source: a source dict with keys corresponding to parameters of this
        object. Typically this dict comes from the 'unfreezing' of a jsonpickle
        file.
      platform_type: The platform type of the object being copied.

    Returns:
      No return value
    """
    self.sheet_url = source['sheet_url']
    self.sheet_id = source['sheet_id']

    self.json_auth_file = source['json_auth_file']
    self._platform_type = platform_type

    if self._platform_type == bid2x_var.PlatformType.DV:
      self.column_status = source['column_status']
      self.column_lineitem_id = source['column_lineitem_id']
      self.column_lineitem_name = source['column_lineitem_name']
      self.column_lineitem_type = source['column_lineitem_type']
      self.column_campaign_id = source['column_campaign_id']
      self.column_advertiser_id = source['column_advertiser_id']
      self.column_custom_bidding = source['column_custom_bidding']
      self.debug = source['debug']
      self.clear_onoff = source['clear_onoff']

  def update_cb_scripts_tab(
      self, zone: Any, cust_bidding_function_string: str, test_run: bool
  ) -> bool:
    """Method to update CB_Scripts status tab.

    Args:
      zone: A bid2x_model object containing (most importantly for this method)
            the rows and columns within the status tab to update.
      cust_bidding_function_string: The string that was generated for the
                                    update or test.
      test_run: A Boolean indicating that the call is for a test when True.
                Otherwise it is assumed that the call is being made in
                conjunction with an update to the actual script.
    Returns:
      True on successful completion of the function.
    """
    # Update CB_Scripts tab
    # Spreadsheet tab name should match key in dict.
    try:
      print('custom bidding')
      print(cust_bidding_function_string)
      cbscripts_sheet = self.gc.open_by_key(self.sheet_id).worksheet(
          'CB_Scripts'
      )
    except gspread.exceptions.SpreadsheetNotFound:
      print('Error: Spreadsheet not found for worksheet CB_Scripts.')
      raise  # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound as e:
      print(f'Error connecting to worksheet CB_Scripts: {e}')
      raise  # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print(
          'Error communicating with Google Sheets API for ',
          f'worksheet CB_Scripts: {e}',
      )
      raise  # Reraises the exception.
    except TimeoutError:
      print('Request timed out. Please check your network connection.')
      raise  # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected error occurred: {e}')
      raise  # Reraises the exception.
    # Work out the row and column for this update.
    if not test_run:
      update_row = zone.update_row
      update_col = chr(Bid2xSpreadsheet.COLUMN_OFFSET + zone.update_col)
    else:
      update_row = zone.test_row
      update_col = chr(Bid2xSpreadsheet.COLUMN_OFFSET + zone.test_col)
    # Write the most recent custom bidding function to the right
    # place on the CB_Scripts tab.
    if update_row:
      current_datetime = datetime.datetime.now()
      try:
        cbscripts_sheet.update(
            values=[[cust_bidding_function_string, f'{current_datetime}']],
            range_name=f'{update_col}{update_row}',
        )
      except Exception as e:
        print(f'Error updating test run into worksheet: {e}')
        raise  # Reraises the exception.
    return True
