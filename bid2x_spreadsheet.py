import json
import gspread
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError

class bid2x_spreadsheet():

  __sheet_url = None
  sheet_id = None
  __sheets_service = None
  __json_auth_file = None
  __column_status = None
  __column_lineitemid = None
  __column_lineitemname = None
  __column_lineitemtype = None
  __column_campaignid = None
  __column_advertiserid = None
  __column_custombidding = None
  __debug = None
  __clear_onoff = None
  gc = None


  def __init__(self,sheet_id, auth_file, debug=False):
    self.sheet_id = sheet_id
    self.__sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/edit'
    self.__json_auth_file = auth_file
    self.__sheets_service = None
    self.__column_status = 'A'
    self.__column_lineitemid = 'B'
    self.__column_lineitemname = 'C'
    self.__column_lineitemtype = 'D'
    self.__column_campaignid = 'E'
    self.__column_advertiserid = 'F'
    self.__column_custombidding = 'K'
    self.__debug = debug
    self.__clear_onoff = True
    self.gc = gspread.service_account(filename=auth_file)



  def __str__(self):
    print(f'SheetID:{self.sheet_id},')
    print(f'sheet_service:{self.__sheets_service},')


  def setName(self,str):
    self.sheet_id = str


  def read_dv_line_items (self, service, line_item_name_pattern, zone_array, defer_pattern):
    """Read DV360 line items and populate

    Args:

    Returns:
      Returns True if able to get to the end of the function
    """
    # Connect to Sheets.
    spreadsheet_id = self.sheet_id

    # Walk the array of bid2x_model objects and do lookups in DV360 to gather line items.
    for zone in zone_array:

      if self.__debug:
        print(f'Current zone object is: {zone.name}')

      # Clear the sheet in the range A2:F1000.
      self.clear_sheet(zone.name, self.__json_auth_file)

      # Generate the string to filter this query by.
      filter_string = f'campaignId={zone.campaign_id}'

      if self.__debug:
        print(f'Generated filter string is: {filter_string}')

      # Ask DV360 for a list of line items for this advertiser where
      # the campaignId = the value for this loop.
      try:
        line_items = service.advertisers().lineItems().list(
            advertiserId=f'{zone.advertiser_id}',
            pageSize=200,
            filter=filter_string).execute()
      # TODO: b/360401055 - Update HTTPError Exception cases.
      except HttpError as e:
        print(f'HttpError with DV360 while listing line items for advertiser {zone.advertiser_id}: {e}')
        raise  # Reraise the exception for higher-level handling
      except GoogleAPICallError as e:
        print(f'Google API error occurred while listing line items for advertiser {zone.advertiser_id}: {e}')
        raise  # Reraise the exception
      except TimeoutError:
        print(f'Request timed out while listing line items for advertiser {zone.advertiser_id}. Please check your network connection.')
        raise  # Reraise the exception

      if self.__debug:
        json_pretty_print = json.dumps(line_items, indent=2)
        # print(f"all line items returned = {json_pretty_print}")
        line_item_length = len(line_items['lineItems'])
        print(f'length of line_items: {line_item_length}')
        for line_item in line_items['lineItems']:
          print(f"{line_item['lineItemId']} - {line_item['displayName']}")

      # Walk results and prep an array for use with Google Sheets update.
      line_items_data = []
      auto_ons_data = []
      for line_item in line_items['lineItems']:
        # Generate the rows of line item data for transfer to Google Sheets
        # except do not allow line item types that are YouTube related.
        if line_item['lineItemType'] not in \
          ('LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_NON_SKIPPABLE',
          'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_REACH',
          'LINE_ITEM_TYPE_YOUTUBE_AND_PARTNERS_ACTION'):
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
        print(f'Error with gspread: Worksheet "{zone.name}" not found in the spreadsheet.')
        raise  # Reraise the exception
      except gspread.exceptions.APIError as e:
        print(f'Error with gspread while connecting to tab "{zone.name}": {e}')
        raise  # Reraise the exception
      except TimeoutError:
        print(f'Request timed out while connecting to tab "{zone.name}". Please check your network connection.')
        raise  # Reraise the exception
      except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred while connecting to tab "{zone.name}": {e}')
        raise  # Reraise the exception

      try:
        current_tab.update(values=line_items_data, range_name=f'{self.__column_status}2')  # Update starting from A2 (row 2).
      except gspread.exceptions.APIError as e:
        print(f"Error communicating with Google Sheets API while updating tab f{zone.name}:{e}")
        raise # Reraises the exception.
      except TimeoutError:
        print(f'Request timed out while updating tab f{zone.name}:{e}. Please check your network connection.')
        raise # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(f"Error with gspread while updating tab f{zone.name}:{e}")
        raise # Reraises the exception.

      # Optionally auto-enable line items matching pattern.
      if not defer_pattern:
        try:
          # Update starting from K2 (row 2).
          current_tab.update(values=auto_ons_data, range_name=f'{self.__column_custombidding}2')

        except gspread.exceptions.APIError as e:
          print(f'Error with gspread while updating range {self.__column_custombidding}2: {e}')
          raise  # Reraises the exception
        except TimeoutError:
          print(f'Request timed out while updating range {self.__column_custombidding}2. Please check your network connection.')
          raise  # Reraises the exception
        except gspread.exceptions.GSpreadException as e:
          print(f'An unexpected gspread error occurred while updating range {self.__column_custombidding}2: {e}')
          raise  # Reraises the exception

    return True


  def get_affected_line_items_from_sheet(self, zone_string, __json_auth_file):
    # Connect to Sheets.
    spreadsheet_id = self.sheet_id

    # Spreadsheet tab name should match key in dict.
    try:
      current_tab = self.__gc.open_by_key(spreadsheet_id).worksheet(zone_string)
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Error with gspread: Spreadsheet with ID {spreadsheet_id} not found.')
      raise  # Reraise the exception for higher-level handling
    except gspread.exceptions.WorksheetNotFound:
        print(f'Error with gspread: Worksheet "{zone_string}" not found in the spreadsheet.')
        raise  # Reraise the exception
    except gspread.exceptions.APIError as e:
        print(f'Error with gspread while connecting to tab "{zone_string}": {e}')
        raise  # Reraise the exception
    except TimeoutError:
        print(f'Request timed out while connecting to tab "{zone_string}". Please check your network connection.')
        raise  # Reraise the exception
    except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred while connecting to tab "{zone_string}": {e}')
        raise  # Reraise the exception

    try:
      list_of_dicts = current_tab.get_all_records()
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred during get_all_records() call: {e}')
      raise  # Reraise the exception for higher-level handling
    except ValueError as e:
        print(f'Error with gspread during get_all_records() call. Data might be improperly formatted: {e}')
        raise  # Reraise the exception

    processed_line_items = [];
    i = 0
    for row in list_of_dicts:
      if row['Generate Custom Bidding'].lower() == 'yes':
        if processed_line_items.count(row["Line Item ID"]) == 0:
          processed_line_items.append(row['Line Item ID'])

    return processed_line_items

  def clear_sheet(self, zone_string, __json_auth_file):
    # Connect to Sheets
    # Spreadsheet tab name should the name of the bid2Model iteam (.name).
    spreadsheet_id = self.sheet_id
    try:
      current_tab = self.gc.open_by_key(spreadsheet_id).worksheet(zone_string)
    except gspread.exceptions.SpreadsheetNotFound:
      print(f'Error with gspread: Spreadsheet with ID {spreadsheet_id} not found.')
      raise # Reraises the exception.
    except gspread.exceptions.WorksheetNotFound:
      print(f'Error with gspread: Worksheet "{zone_string}" not found in the spreadsheet.')
      raise # Reraises the exception.
    except gspread.exceptions.APIError as e:
      print(f'Error with gspread while connecting to tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except TimeoutError:
      print(f'Request timed out while connecting to tab "{zone_string}". Please check your network connection.')
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred while connecting to tab "{zone_string}": {e}')
      raise # Reraises the exception.

    try:
      current_tab.batch_clear([f'{self.__column_status}2:{self.__column_advertiserid}1000'])
    except gspread.exceptions.APIError as e:
      print(f'Error with gspread during batch_clear operation on tab "{zone_string}": {e}')
      raise # Reraises the exception.
    except gspread.exceptions.GSpreadException as e:
      print(f'An unexpected gspread error occurred during batch_clear on tab "{zone_string}": {e}')
      raise # Reraises the exception.

    # Build array of 'No' values for column in spreadsheet to
    # clear out the custom bidding 'Yes' selections.
    if self.__clear_onoff:
      onOff_Array = []
      onOff_Array = [['No']]*999
      try:
        current_tab.update(values=onOff_Array, range_name=f'{self.__column_custombidding}2')
      except gspread.exceptions.APIError as e:
        print(f'Error with gspread during update of range {self.__column_custombidding}2 on tab "{zone_string}": {e}')
        raise # Reraises the exception.
      except gspread.exceptions.GSpreadException as e:
        print(f'An unexpected gspread error occurred during update on tab "{zone_string}": {e}')
        raise # Reraises the exception.