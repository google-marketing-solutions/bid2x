from http import HTTPStatus
from click import clear
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import HttpRequest
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError
from typing import Any
from bid2x_util import *

import time
import gspread


from bid2x_model import bid2x_model
import bid2x_var

class bid2x_spreadsheet():

  sheet_url: str
  sheet_id: int
  sheets_service = None
  json_auth_file: str
  column_status: str
  column_lineitemid: str
  column_lineitemname: str
  column_lineitemtype: str
  column_campaignid: str
  column_advertiserid: str
  column_custombidding: str
  debug: bool
  clear_onoff: bool
  gc: gspread

  def __init__(self,sheet_id: str, auth_filename: str):
    self.sheet_id = sheet_id
    self.sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
    self.json_auth_file = auth_filename
    self.sheets_service = None
    self.column_status = 'A'
    self.column_lineitemid = 'B'
    self.column_lineitemname = 'C'
    self.column_lineitemtype = 'D'
    self.column_campaignid = 'E'
    self.column_advertiserid = 'F'
    self.column_custombidding = 'K'
    self.debug = False
    self.clear_onoff = True
    self.gc = gspread.service_account(filename=auth_filename)

  def __str__(self) -> None:
    print(f'SheetID:{self.sheet_id},')
    print(f'sheet_service:{self.sheet_service},')
    print(f'gc:{self.gc},')

  def set_name(self, name:str) -> None:
    self.sheet_id = name

  def read_dv_line_items (self,
                          service: Any,
                          line_item_name_pattern: str,
                          zone_array: bid2x_model,
                          defer_pattern: bool) -> bool:

    """Read DV360 line items and populate the associated spreadsheet's
       tabs with information from client's account structure in DV.
    Args:
      service - DV360 connection object
      line_item_name_pattern - A string containing a pattern to match in
                               line item names.  Those line items with names
                               containing substrings with this value will be
                               by default turned 'on' in the spreadsheet
                               and for use with this system.
      zone_array - array of bid2x_model objects describing all the zones or
                   campaigns that are in use.
      defer_pattern - A Boolean that, when true, does not use the line_item_
                      name_pattern string variable to match against line
                      item name substrings, but rather, leaves the on/off
                      status of the line items listed as untouched.
    Returns:
      Returns True if able to get to the end of the function.
    """
    # Connect to Sheets.
    # gc = gspread.service_account(filename=self.json_auth_file)
    spreadsheet_id = self.sheet_id

    # We require a valid zone_array and a valid spreadsheet to continue,
    # if either are missing then return from this method
    if not zone_array or not spreadsheet_id:
      return False

    # Walk the array of bid2x_model objects and do
    # lookups in DV360 to gather line items.
    for zone in zone_array:

      if self.debug:
        print(f'Current zone object is: {zone.name}')

      # Clear the sheet in the range A2:F1000.
      self.clear_sheet(zone.name, self.json_auth_file)

      # Generate the string to filter this query by.
      filter_string = f'campaignId={zone.campaign_id}'

      # Ask DV360 for a list of line items for this advertiser where
      # the campaignId = the value for this loop.
      # TODO: Known issue here when the number of line items exceeds
      # the page size of LARGE_PAGE_SIZE (200).  
      # The code should retrieve a page at a time until
      # all the line items are exhausted.
      request = service.advertisers().lineItems().list(
        advertiserId=f'{zone.advertiser_id}',
        pageSize=bid2x_var.LARGE_PAGE_SIZE,
        filter=filter_string)

      try:
        line_items = request.execute()
      # TODO: b/360401055 - Update HTTPError Exception cases.
      except HttpError as e:
        print(f'HttpError with DV360 while listing line items ',
              f'for advertiser {zone.advertiser_id}: {e}')
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
          line_items = request.execute()
        else:
          raise
      except GoogleAPICallError as e:
        print(f'Google API error occurred while listing line items ',
              f'for advertiser {zone.advertiser_id}: {e}')
        raise  # Reraise the exception
      except TimeoutError:
        print(f'Request timed out while listing line items for advertiser ',
              f'{zone.advertiser_id}. Please check your network connection.')
        raise  # Reraise the exception

      # Walk results and prep an array for use with Google Sheets update.
      line_items_data = []
      auto_ons_data = []
      for line_item in line_items['lineItems']:
        # Generate the rows of line item data for transfer to Google Sheets
        # except do not allow line item types that are YouTube related.
        if line_item['lineItemType'] not in \
          ('LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_NON_SKIPPABLE',
          'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_REACH',
          'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_ACTION') and \
          line_item_name_pattern in line_item['displayName']:

          line_items_data.append([
              line_item['entityStatus'],
              line_item['lineItemId'],
              line_item['displayName'],
              line_item['lineItemType'],
              line_item['campaignId'],
              line_item['advertiserId']
              ])

          # Build array for optional auto_on.
          if line_item_name_pattern in line_item['displayName']:
            auto_ons_data.append(['Yes'])
          else:
            auto_ons_data.append(['No'])

      # Spreadsheet tab name should be the name of the bid2x_model item (.name).
      try:
        current_tab = self.gc.open_by_key(spreadsheet_id).worksheet(zone.name)
      except gspread.exceptions.SpreadsheetNotFound:
        print(f'Error with gspread: Spreadsheet with ID {spreadsheet_id} not found.')
        raise  # Reraise the exception for higher-level handling
      except gspread.exceptions.WorksheetNotFound:
        print(f'Error with gspread: Worksheet "{zone.name}" ',
              f'not found in the spreadsheet.')
        raise  # Reraise the exception
      except gspread.exceptions.APIError as e:
        print(f'Error with gspread while connecting to tab "{zone.name}": {e}')
        raise  # Reraise the exception
      except TimeoutError:
        print(f'Request timed out while connecting to tab "{zone.name}". ',
              f'Please check your network connection.')
        raise  # Reraise the exception
      except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred while connecting ',
              f'to tab "{zone.name}": {e}')
        raise  # Reraise the exception
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
          current_tab = self.gc.open_by_key(
            spreadsheet_id).worksheet(zone.name)
        else:
          raise

      try:
        # Update starting from A2 (row 2).
        current_tab.update(values=line_items_data,
                           range_name=f'{self.column_status}2')
      except gspread.exceptions.APIError as e:
        print(f"Error communicating with Google Sheets API while ",
              f"updating tab f{zone.name}:{e}")
        raise # Reraises the exception.
      except TimeoutError:
        print(f'Request timed out while updating tab f{zone.name}:{e}. ',
              f'Please check your network connection.')
        raise # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(f"Error with gspread while updating tab f{zone.name}:{e}")
        raise # Reraises the exception.
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
          current_tab.update(values=line_items_data,
                             range_name=f'{self.column_status}2')
        else:
          raise

      # Optionally auto-enable line items matching pattern.
      if not defer_pattern:
        try:
          # Update starting from K2 (row 2).
          current_tab.update(values=auto_ons_data,
                             range_name=f'{self.column_custombidding}2')
        except gspread.exceptions.APIError as e:
          print(f'Error with gspread while updating range ',
                f'{self.__column_custombidding}2: {e}')
          raise  # Reraises the exception
        except TimeoutError:
          print(f'Request timed out while updating range ',
                f'{self.__column_custombidding}2. ',
                f'Please check your network connection.')
          raise  # Reraises the exception
        except gspread.exceptions.GSpreadException as e:
          print(f'An unexpected gspread error occurred while updating ',
                f'range {self.__column_custombidding}2: {e}')
          raise  # Reraises the exception
        except HttpError as err:
          # If the error is a rate limit or connection error,
          # wait and try again.
          if is_recoverable_http_error(err.resp.status):
            time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
            current_tab.update(values=auto_ons_data,
                               range_name=f'{self.column_custombidding}2')
          else:
            raise

    return True

  def get_affected_line_items_from_sheet(self,
                                         zone_string: str) -> list[int]:
    # Get reference to already connected Sheets.
    spreadsheet_id = self.sheet_id
    # Open the spreadsheet tab name that is the passed zone string.
    try:
      current_tab = self.gc.open_by_key(
        spreadsheet_id).worksheet(zone_string)
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Error with gspread: Spreadsheet with ',
            f'ID {spreadsheet_id} not found.')
      raise  # Reraise the exception for higher-level handling
    except gspread.exceptions.WorksheetNotFound:
        print(f'Error with gspread: Worksheet "{zone_string}" not ',
              f'found in the spreadsheet.')
        raise  # Reraise the exception
    except gspread.exceptions.APIError as e:
        print(f'Error with gspread while connecting to ',
              f'tab "{zone_string}": {e}')
        raise  # Reraise the exception
    except TimeoutError:
        print(f'Request timed out while connecting to tab "{zone_string}". ',
              f'Please check your network connection.')
        raise  # Reraise the exception
    except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred while ',
              f'connecting to tab "{zone_string}": {e}')
        raise  # Reraise the exception
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        current_tab = self.gc.open_by_key(
          spreadsheet_id).worksheet(zone_string)
      else:
        raise

    # Get list of all records on the opened spreadsheet.
    try:
      list_of_dicts = current_tab.get_all_records()
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred during ',
            f'get_all_records() call: {e}')
      raise  # Reraise the exception for higher-level handling
    except ValueError as e:
        print(f'Error with gspread during get_all_records() call. ',
              f'Data might be improperly formatted: {e}')
        raise  # Reraise the exception
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        list_of_dicts = current_tab.get_all_records()
      else:
        raise

    # Create an epmty list of processed line items.
    # Some Line Items may be disabled, we are building a list of line item
    # IDs that are enabled for the custom bidding to pass back.
    processed_line_items = []
    for row in list_of_dicts:
      # TODO: change these static texts to variables.  For now the
      # spreadsheet columns are bound to these names.
      if row['Generate Custom Bidding'].lower() == 'yes':
        if processed_line_items.count(row["Line Item ID"]) == 0:
          processed_line_items.append(row['Line Item ID'])

    return processed_line_items

  def clear_sheet (self,
                   zone_string: str,
                   json_auth_file: str) -> bool:

    # Get reference to already connected Sheets.
    spreadsheet_id = self.sheet_id
    try:
      # Spreadsheet tab name is the name of the bid2Model iteam (.name).
      current_tab = self.gc.open_by_key(
        spreadsheet_id).worksheet(zone_string)
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Error with gspread: Spreadsheet with ',
            f'ID {spreadsheet_id} not found.')
      raise # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound:
      print(f'Error with gspread: Worksheet "{zone_string}" ',
            f'not found in the spreadsheet.')
      raise # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print(f'Error with gspread while connecting to tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except TimeoutError:
      print(f'Request timed out while connecting to tab "{zone_string}". ',
            f'Please check your network connection.')
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred while ',
            f'connecting to tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        current_tab = self.gc.open_by_key(
          spreadsheet_id).worksheet(zone_string)
      else:
        raise

    # Build the address string containing the range used
    # to 'clear' the spreadsheet
    clear_string = f'{self.column_status}'
    clear_string += f'{bid2x_var.SPREADSHEET_FIRST_DATA_ROW}'
    clear_string += ':'
    clear_string += f'{self.column_advertiserid}'
    clear_string += f'{bid2x_var.SPREADSHEET_LAST_DATA_ROW}'

    # Perform batch clear operation.
    try:
      current_tab.batch_clear([clear_string])
    except gspread.exceptions.APIError as e:
      print(f'Error with gspread during batch_clear operation ',
            f'on tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred during batch_clear ',
            f'on tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except HttpError as err:
      # If the error is a rate limit or connection error,
      # wait and try again.
      if is_recoverable_http_error(err.resp.status):
        time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
        current_tab.batch_clear([clear_string])
      else:
        raise

    # Build array of 'No' values for column in spreadsheet to
    # clear out the custom bidding 'Yes' selections.
    if self.clear_onoff:
      onOff_Array = []
      onOff_Array = [['No']]*(bid2x_var.SPREADSHEET_LAST_DATA_ROW -
                              bid2x_var.SPREADSHEET_FIRST_DATA_ROW)
      try:
        current_tab.update(
          values=onOff_Array, range_name=f'{self.column_custombidding}2')
      except gspread.exceptions.APIError as e:
        print(f'Error with gspread during update of ',
              f'range {self.__column_custombidding}',
              f'{bid2x_var.SPREADSHEET_FIRST_DATA_ROW} on',
              f'tab "{zone_string}": {e}')
        raise # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred during update ',
              f'on tab "{zone_string}": {e}')
        raise # Reraises the exception.
      except HttpError as err:
        # If the error is a rate limit or connection error,
        # wait and try again.
        if is_recoverable_http_error(err.resp.status):
          time.sleep(bid2x_var.HTTP_RETRY_TIMEOUT)
          current_tab.update(
            values=onOff_Array, range_name=f'{self.column_custombidding}2')
        else:
          raise

    return True
