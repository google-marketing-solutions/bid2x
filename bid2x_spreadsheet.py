from typing import Any
import time
from datetime import datetime
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError
import gspread
from bid2x_util import *
import bid2x_var


class bid2x_spreadsheet():

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
    clear_onoff: bool
    gc: gspread
    COLUMN_OFFSET = 64          # Add to column # to get actual column letter.
    MAX_RETRIES = 5             # Number of retries when API calls fail

    def __init__(self,sheet_id: str, auth_filename: str):
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
        self.clear_onoff = True
        # self.gc = gspread.service_account(filename=auth_filename)

    def __str__(self) -> str:
        return_str = (
            f'sheet_id:{self.sheet_id}\n'
            f'sheet_url:{self.sheet_url}\n'
            f'json_auth_file:{self.json_auth_file}\n'
            f'sheets_service:{self.sheets_service}\n'
            f'gc:{self.gc}\n'
            f'debug:{self.debug}\n')

        if self._platform_type == bid2x_var.PlatformType.DV.value:
            return_str = (return_str +
                f'column_status:{self.column_status}\n'
                f'column_lineitem_id:{self.column_lineitem_id}\n'
                f'column_lineitem_name:{self.column_lineitem_name}\n'
                f'column_lineitem_type:{self.column_lineitem_type}\n'
                f'column_campaign_id:{self.column_campaign_id}\n'
                f'column_advertising:{self.column_advertiser_id}\n'
                f'column_custom_bidding:{self.column_custom_bidding}\n'
                f'clear_onoff:{self.clear_onoff}')

        return return_str

    def __getstate__(self):
        state = self.__dict__.copy()  # Start with all attributes.
        del state['gc']               # Remove the gc attribute.
        del state['sheets_service']   # Remove the sheets_service attribute.
        return state                  # Return the modified state dictionary.

    def read_dv_line_items (self,
                            service: Any,
                            line_item_name_pattern: str,
                            zone_array: Any,
                            defer_pattern: bool) -> bool:

        """Read DV360 line items and populate the associated spreadsheet's
          tabs with information from client's account structure in DV.
        Args:
            service - DV360 connection object
            line_item_name_pattern - A string containing a pattern to match in
                                    line item names.  Those line items with
                                    names containing substrings with this value
                                    will be by default turned 'on' in the
                                    spreadsheet and for use with this system.
            zone_array - array of bid2x_model objects describing all the zones
                         or campaigns that are in use.
            defer_pattern - A Boolean that, when true, does not use the
                            line_item_name_pattern string variable to match
                            against line item name substrings, but rather,
                            leaves the on/off status of the line items listed as
                            untouched.
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

            retry_count = 0
            delay = bid2x_var.HTTP_RETRY_TIMEOUT

            while retry_count < bid2x_spreadsheet.MAX_RETRIES:
                try:
                    line_items = request.execute()
                # TODO: Update HTTPError Exception cases.
                except HttpError as e:
                    print(f'HttpError with DV360 while listing line items ',
                          f'for advertiser {zone.advertiser_id}: {e}')
                    # If the error is a rate limit or connection error,
                    # wait and try again.
                    if is_recoverable_http_error(err.resp.status):
                        print(f'Retrying in {delay} seconds...')
                        time.sleep(delay)
                        retry_count += 1
                        delay *= 2

                        # If we get here, we've exceeded the maximum retries
                        if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                            print( 'Failed to list line items after '
                                  f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                            raise
                    else:
                        raise
                except GoogleAPICallError as e:
                    print(f'Google API error occurred while listing line items ',
                          f'for advertiser {zone.advertiser_id}: {e}')
                    raise  # Reraise the exception
                except TimeoutError:
                    print(f'Request timed out while listing line items for ',
                          f'advertiser {zone.advertiser_id}. Please check your '
                          'network connection.')
                    raise  # Reraise the exception

            # Walk results and prep an array for use with Google Sheets update.
            line_items_data = []
            auto_ons_data = []
            for line_item in line_items['lineItems']:
                # Generate the rows of line item data for transfer to Google
                # Sheets except do not allow line item types that are YouTube
                # related.
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

            retry_count = 0
            delay = bid2x_var.HTTP_RETRY_TIMEOUT

            while retry_count < bid2x_spreadsheet.MAX_RETRIES:
                # Spreadsheet tab name should be the name of the bid2x_model
                # item (.name).
                try:
                    current_tab = self.gc.open_by_key(spreadsheet_id). \
                        worksheet(zone.name)
                except gspread.exceptions.SpreadsheetNotFound:
                    print(f'Error with gspread: Spreadsheet with ID '
                          f'{spreadsheet_id} not found.')
                    raise  # Reraise the exception for higher-level handling
                except gspread.exceptions.WorksheetNotFound:
                    print(f'Error with gspread: Worksheet "{zone.name}" ',
                          f'not found in the spreadsheet.')
                    raise  # Reraise the exception
                except gspread.exceptions.APIError as e:
                    print( 'Error with gspread while connecting to tab '
                          f'"{zone.name}": {e}')
                    raise  # Reraise the exception
                except TimeoutError:
                    print( 'Request timed out while connecting to tab '
                          f'"{zone.name}".  Please check your network '
                           'connection.')
                    raise  # Reraise the exception
                except gspread.exceptions.GSpreadException as e:
                    print(f'An unexpected gspread error occurred while '
                          f'connecting to tab "{zone.name}": {e}')
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
                        if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                            print( 'Failed to opening worksheet after '
                                  f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                            raise
                    else:
                        raise

            retry_count = 0
            delay = bid2x_var.HTTP_RETRY_TIMEOUT

            while retry_count < bid2x_spreadsheet.MAX_RETRIES:
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
                        print(f'Retrying in {delay} seconds...')
                        time.sleep(delay)
                        retry_count += 1
                        delay *= 2

                        # If we get here, we've exceeded the maximum retries
                        if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                            print( 'Failed to updating tab after '
                                  f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                            raise

                    else:
                        raise

            # Optionally auto-enable line items matching pattern.
            if not defer_pattern:
                retry_count = 0
                delay = bid2x_var.HTTP_RETRY_TIMEOUT

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
                        print(f'Retrying in {delay} seconds...')
                        time.sleep(delay)
                        retry_count += 1
                        delay *= 2

                        # If we get here, we've exceeded the maximum retries
                        if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                            print( 'Failed to updating range after '
                                  f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                            raise
                    else:
                      raise

        return True

    def get_affected_line_items_from_sheet(self,
                                           zone_string: str) -> list[int]:
        """Gets the data from a single tab within the linked spreadsheet
        and returns all rows where the spreadsheet is marked 'Yes' to
        generate the custom bidding script for that Line Item.
        Args:
          zone_string - a string corresponding to the label on a tab in the
          Google sheet.

        Returns:
          A list of line items that need to be included in the custom bidding.
        """
        # Get reference to already connected Sheets.
        spreadsheet_id = self.sheet_id
        # Open the spreadsheet tab name that is the passed zone string.

        retry_count = 0
        delay = bid2x_var.HTTP_RETRY_TIMEOUT

        while retry_count < bid2x_spreadsheet.MAX_RETRIES:
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
                    print(f'Retrying in {delay} seconds...')
                    time.sleep(delay)
                    retry_count += 1
                    delay *= 2

                    # If we get here, we've exceeded the maximum retries
                    if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                        print( 'Failed to opening worksheet after '
                              f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                        raise
                else:
                    raise

        retry_count = 0
        delay = bid2x_var.HTTP_RETRY_TIMEOUT

        while retry_count < bid2x_spreadsheet.MAX_RETRIES:
            # Get list of all records on the opened spreadsheet.
            try:
                list_of_dicts = current_tab.get_all_records()
            except gspread.exceptions.GSpreadException as e:
                print( 'An unexpected gspread error occurred during ',
                      f'get_all_records() call: {e}')
                raise  # Reraise the exception for higher-level handling
            except ValueError as e:
                print( 'Error with gspread during get_all_records() call. ',
                      f'Data might be improperly formatted: {e}')
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
                    if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                        print( 'Failed to get all records after '
                              f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                        raise
                else:
                    raise

        # Create an empty list of processed line items.
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
        """For the Google Sheet associated with this project, this function
        clears the cells in the passed tab name between the column for
        status and the column for advertiser ID and between the rows defined
        as being the first data row and the last data row (typically this is
        row 2 to row 1000).
        Args:
            zone_string - a string corresponding to the label on a tab in the
            Google sheet.

        Returns:
            True if able to complete the function successfully.
        """
        # Get reference to already connected Sheets.
        spreadsheet_id = self.sheet_id

        retry_count = 0
        delay = bid2x_var.HTTP_RETRY_TIMEOUT

        while retry_count < bid2x_spreadsheet.MAX_RETRIES:
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
                print(f'Error with gspread while connecting to tab '
                      f'"{zone_string}": {e}')
                raise # Reraises the exception.
            except TimeoutError:
                print(f'Request timed out while connecting to tab "{zone_string}"',
                      f'. Please check your network connection.')
                raise # Reraises the exception.
            except gspread.exceptions.GSpreadException as e:
                print(f'An unexpected gspread error occurred while ',
                      f'connecting to tab "{zone_string}": {e}')
                raise # Reraises the exception.
            except HttpError as err:
                # If the error is a rate limit or connection error,
                # wait and try again.
                if is_recoverable_http_error(err.resp.status):
                    print(f'Retrying in {delay} seconds...')
                    time.sleep(delay)
                    retry_count += 1
                    delay *= 2

                    # If we get here, we've exceeded the maximum retries
                    if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                        print( 'Failed to open worksheet after '
                              f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
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

        while retry_count < bid2x_spreadsheet.MAX_RETRIES:
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
                    print(f'Retrying in {delay} seconds...')
                    time.sleep(delay)
                    retry_count += 1
                    delay *= 2

                    # If we get here, we've exceeded the maximum retries
                    if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                        print( 'Failed batch clear operation after '
                              f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                        raise
                else:
                    raise

        # Build array of 'No' values for column in spreadsheet to
        # clear out the custom bidding 'Yes' selections.
        if self.clear_onoff:
            on_off_array = [['No']]*(bid2x_var.SPREADSHEET_LAST_DATA_ROW -
                                    bid2x_var.SPREADSHEET_FIRST_DATA_ROW)

            retry_count = 0
            delay = bid2x_var.HTTP_RETRY_TIMEOUT

            while retry_count < bid2x_spreadsheet.MAX_RETRIES:
                try:
                    current_tab.update(
                      values=on_off_array, range_name=f'{self.column_custom_bidding}2')
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
                        print(f'Retrying in {delay} seconds...')
                        time.sleep(delay)
                        retry_count += 1
                        delay *= 2

                        # If we get here, we've exceeded the maximum retries
                        if retry_count == bid2x_spreadsheet.MAX_RETRIES:
                            print( 'Failed batch clear operation after '
                                  f'{bid2x_spreadsheet.MAX_RETRIES} attempts.')
                            raise
                    else:
                        raise

        return True


    def update_cb_scripts_tab(self,
                              zone: Any,
                              cust_bidding_function_string: str,
                              test_run: bool)->bool:
        """This method updates the spreadsheet status tab (usually called
          'CB Scripts') with the most recent script uploads and script tests
          that are run using the system.  This tab provides a convenient way
          to see the recent changes to all custom bidding scripts.
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
        update_row = None
        try:
            cbscripts_sheet = \
                self.gc.open_by_key(self.sheet_id).worksheet("CB_Scripts")
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

        # Work out the row and column for this update.
        if not test_run:
            update_row = zone.update_row
            update_col = chr(bid2x_spreadsheet.COLUMN_OFFSET + zone.update_col)
        else:
            update_row = zone.test_row
            update_col = chr(bid2x_spreadsheet.COLUMN_OFFSET + zone.test_col)

        # Write the most recent custom bidding function to the right
        # place on the CB_Scripts tab.
        if update_row:
            try:
                cbscripts_sheet.update(
                    values=[[cust_bidding_function_string,f"{datetime.now()}"]],
                    range_name=f'{update_col}{update_row}')
            except Exception as e:
                print(f'Error updating test run into worksheet: {e}')
                raise # Reraises the exception.

        return True

    def top_level_copy(self,source: Any, platform_type: str)->None:
        """This method makes a copy of top-level parameters within the source
        dict to the current object.  The jsonpickle process, when loading a
        configuration, returns a dict whose keys correspond to parameters
        within this object.

        Args:
          source: a source dict with keys corresponding to parameters of this
          object. Typically this dict comes from the 'unfreezing' of a
          jsonpickle file.
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

