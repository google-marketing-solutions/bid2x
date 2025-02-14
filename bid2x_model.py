"""BidToX - bid2x_model application module.

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

  This module contains the bid2x_model class which is used to
  represent a zone in the Bid2X system.  It contains the necessary
  information to run the system and perform the necessary lookups
  in DV360 and Google Tag Manager.
"""

from typing import Any

from bid2x_util import google_dv_call
from googleapiclient import http


HttpRequest = http.HttpRequest
MediaFileUpload = http.MediaFileUpload


class Error(Exception):
  """Base exception for Bid2xModel."""


class Bid2xModel():
  """GTM object for DV zone model.

    Attributes:
        name: str
        campaign_id: int
        advertiser_id: int
        algorithm_id: int
        cb_algorithm: str
        debug: bool
        update_row: int
        update_col: int
        test_row: int
        test_col: int

    Methods:
      __init__:
      __str__:
      set_name:
      set_spreadsheet_row_col:
      set_cb_algorithm:
      update_custom_bidding_scripts:

  """

  # Attributes
  name: str
  campaign_id: int
  advertiser_id: int
  algorithm_id: int
  cb_algorithm: str
  debug: bool
  update_row: int
  update_col: int
  test_row: int
  test_col: int

  def __init__(self, name: str, campaign_id: int, advertiser_id: int,
               algorithm_id: int, debug: bool, update_row: int,
               update_col: int, test_row: int, test_col: int):
    self.name = name
    self.campaign_id = campaign_id
    self.advertiser_id = advertiser_id
    self.algorithm_id = algorithm_id
    self.cb_algorithm = ''  # Initially set to empty string.
    self.debug = debug
    self.update_row = update_row
    self.update_col = update_col
    self.test_row = test_row
    self.test_col = test_col

  def __str__(self)->str:
    """Override str method for this object to return a sensible string.

    Args:
       None
    Returns:
       A formatted string containing the main object properties.
    """
    zone_str = (
        f'Zone Name: {self.name}\n'
        f'\tadvertiser_id: {self.advertiser_id},\n'
        f'\tcampaign_id: {self.campaign_id},\n'
        f'\talgorithm_id: {self.algorithm_id}\n'
        f'\tcb_algorithm: {self.cb_algorithm}\n'
        f'\tupdate_row: {self.update_row}\n'
        f'\tupdate_col: {self.update_col}\n'
        f'\ttest_row: {self.test_row}\n'
        f'\ttest_col: {self.test_col}\n'
    )

    return zone_str

  def set_name(self, name: str) -> None:
    self.name = name

  def set_spreadsheet_row_col(self,
                              update_row: int,
                              update_col: int,
                              test_row: int,
                              test_col: int)->None:
    """Setter function for row and col variables.

    Args:
      update_row: The row number to use for an update string when the
                  custom bidding algorithm is changed (--au argument)
      update_col: The column number (not letter) to use for an update string
                  when the custom bidding algorithm is changed.
      test_row:   The row number to use for an update string when a
                  test is run (--at argument).
      test_col:   The column number (not letter) to use for an update string
                   when a test is run.
    Returns:
      None
    """
    self.update_row = update_row
    self.update_col = update_col
    self.test_row = test_row
    self.test_col = test_col

  def set_cb_algorithm(self, str_algor: str) -> None:
    self.cb_algorithm = str_algor

  def update_custom_bidding_scripts(self,
                                    service: Any,
                                    advertiser_id: int,
                                    algorithm_id: int,
                                    script_path: str,
                                    line_item_array: list[int]) -> bool:
    """Upload a new script to an EXISTING custom bidding algorithm.

      First, a custom bidding script reference is created.  This is a
      resrouceName used in the next step in this function.
      Next, the resourceName from the first step is used to upload the
      script that is stored in a local file.
      Finally, after successful upload of the file the resource is associated
      with the custom bidding algorithm and applied to the various line item
      ids that it will work with.
    Args:
      service: an active service connection object to DV360
      advertiser_id: the advertiser ID to upload c.b algorithm for
      algorithm_id: the custom bidding algorithm the script will be
                  uploaded to.
      script_path: a string containing the path within the local filesystem
                  where the script can be loaded from.  In a previous
                  step it is expected that the generated script is written
                  to storage.
      line_item_array: a list of line item ids to apply the
      new custom bidding algorithm to.

    Returns:
      true on completion of function
    """
    # Part 1 - upload script and get a reference ID.
    # Retrieve a usable custom bidding script reference object.
    create_script_ref_request = service.customBiddingAlgorithms().uploadScript(
        customBiddingAlgorithmId=f'{algorithm_id}',
        advertiserId=f'{advertiser_id}',
    )
    custom_bidding_script_ref = google_dv_call(
        create_script_ref_request, 'create c.b. script reference'
    )
    # Display the new custom bidding script reference object.
    if self.debug:
      print(
          'The following custom bidding script reference object was retrieved:'
          f'{custom_bidding_script_ref}'
      )

    # Part 2 - upload script file.
    # Create a media upload object.
    media = MediaFileUpload(script_path)
    # Create upload request.
    upload_request = service.media().upload(
        resourceName=custom_bidding_script_ref['resourceName'], media_body=media
    )
    # Override response handler to expect null response.
    upload_request.postproc = HttpRequest.null_postproc
    # Upload script to resource location given in retrieved custom bidding
    # script reference object.
    upload_response = google_dv_call(upload_request, 'upload c.b. script')

    if self.debug:
      print(f'response from upload of media: {upload_response}.')

    # Part 3 - Create a custom bidding script object.
    script_obj = {'script': custom_bidding_script_ref}
    # Create the custom bidding script.
    create_cb_scrpt_request = (
        service.customBiddingAlgorithms()
        .scripts()
        .create(
            customBiddingAlgorithmId=f'{algorithm_id}',
            advertiserId=f'{advertiser_id}',
            body=script_obj,
        )
    )
    create_cb_scrpt_response = google_dv_call(
        create_cb_scrpt_request, 'create c.b. script'
    )
    # Display the new custom bidding script object.
    if self.debug:
      print(
          'The following custom bidding script was created: ',
          f'{create_cb_scrpt_response}',
      )

    # Part 4 - Assign script to a custom bidding algorithm.
    # Create the new bid strategy object.
    bidding_strategy = {
        'maximizeSpendAutoBid': {
            'performanceGoalType': (
                'BIDDING_STRATEGY_PERFORMANCE_GOAL_TYPE_CUSTOM_ALGO'
            ),
            'customBiddingAlgorithmId': algorithm_id,
        }
    }
    # Create a line item object assigning the new bid strategy.
    line_item_obj = {'bidStrategy': bidding_strategy}

    # Bulk update preparation.

    # Create a list of line item strings.
    str_list_of_li = list(map(str, line_item_array))

    # Format the body object.
    body_obj = {
        'lineItemIds': [str_list_of_li],
        'targetLineItem': line_item_obj,
        'updateMask': 'bidStrategy',
    }

    li_update_request = (
        service.advertisers()
        .lineItems()
        .bulkUpdate(advertiserId=f'{advertiser_id}', body=body_obj)
    )

    li_update_response = google_dv_call(
        li_update_request, 'bulk add line items to algorithm'
    )

    if self.debug:
      # Display the response from the line item bulk update.
      print('Line Items update request: '
            f'{li_update_response["updatedLineItemIds"]}'
            )

    return True
