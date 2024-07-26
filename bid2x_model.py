from googleapiclient.http import MediaFileUpload
from googleapiclient.http import HttpRequest
from googleapiclient.errors import HttpError
from google.api_core.exceptions import GoogleAPICallError

class Bid2xModelError(Exception):
  """Base exception for Bid2xModel."""
  pass

class bid2x_model():
  name = None
  campaign_id = None
  advertiser_id = None
  algorithm_id = None
  cb_algorithm = None
  debug = None

  def __init__(self, name, campaign_id, advertiser_id, algorithm_id, debug):
    self.name = name
    self.campaign_id = campaign_id
    self.advertiser_id = advertiser_id
    self.algorithm_id = algorithm_id
    self.debug = debug

  def __str__(self):
    print(f'Name:{self.name},')
    print(f'AdvertiserID:{self.advertiser_id},')
    print(f'CampaignID:{self.campaign_id},')
    print(f'AlgorithmID:{self.algorithm_id}')
    print(f'CBAlgorithm:{self.cb_algorithm}')

  def setName(self,str):
    self.name = str

  def setCBAlgorithm (self,str_algor):
    self.cb_algorithm = str_algor

  def updateCustomBiddingScripts(self, service, advertiser_id, algorithm_id, script_path,
                                 line_item_array):
    """This function takes the steps necessary to upload a new script to
      AN EXISTING custom bidding algorithm.

      First, a custom bidding script reference is created.  This is a
      resrouceName used in the next step in this function.
      Next, the resourceName from the first step is used to upload the
      script that is stored in a local file.
      Finally, after successful upload of the file the resource is associated
      with the custom bidding algorithm and applied to the various line item
      ids that it will work with.

    Args:
      service: an active service connection object to DV360
      advertiserId: the advertiser ID to upload c.b algorithm for
      algorithmId: the custom bidding algorithm the script will be
                  uploaded to.
      script_path: a string containing the path within the local filesystem
                  where the script can be loaded from.  In a previous
                  step it is expected that the generated script is written
                  to storage.

    Returns:
      0 on completion of function
    """
    # Part 1 - upload script and get a reference ID.

    # Retrieve a usable custom bidding script reference
    # object.
    try:
      custom_bidding_script_ref = service.customBiddingAlgorithms().uploadScript(
          customBiddingAlgorithmId=f'{algorithm_id}',
          advertiserId=f'{advertiser_id}'
          ).execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      # Handle HTTP errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, etc.)
      print(f'HttpPError occurred creating custom bidding script reference: {e}')
      raise Bid2xModelError('HttPError occurred while creating custom bidding script') from e
    except GoogleAPICallError as e:
      # Handle more specific Google API errors
      print(f'Google API error occurred while creating custom bidding script reference: {e}')
      raise Bid2xModelError('Google API error occurred while error creating custom bidding script reference') from e

    # Display the new custom bidding script reference object.
    if self.debug:
      print('The following custom bidding script reference object was retrieved:'
            f'{custom_bidding_script_ref}')

    # Part 2 - upload script file.

    # Create a media upload object.
    media = MediaFileUpload(script_path)

    try:
      # Create upload request.
      upload_request = service.media().upload(
          resourceName=custom_bidding_script_ref['resourceName'],
          media_body=media)

      # Override response handler to expect null response.
      upload_request.postproc = HttpRequest.null_postproc

      # Upload script to resource location given in retrieved custom bidding
      # script reference object.
      upload_request.execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      print(f'HttpError occurred while uploading script: {e}')
      raise Bid2xModelError('HttpError occurred while uploading script') from e  # Chain the exception for better context
    except GoogleAPICallError as e:
      print(f'Google API error occurred while uploading the script: {e}')
      raise Bid2xModelError('Error uploading script') from e  # Chain the exception
    except TimeoutError:
      print(f'Request timed out while uploading the script. Please check your network connection.  {e}')
      raise Bid2xModelError('Error uploading script') from e
    except OSError as e:
      print(f'An error occurred while reading the script file: {e}')
      raise Bid2xModelError('Error uploading script') from e

    # Part 3 - Create a custom bidding script object.

    script_obj = {
        'script': custom_bidding_script_ref
    }

    # Create the custom bidding script.
    try:
      response = service.customBiddingAlgorithms().scripts().create(
          customBiddingAlgorithmId=f'{algorithm_id}',
          advertiserId=f'{advertiser_id}',
          body=script_obj).execute()
    # TODO: b/360401055 - Update HTTPError Exception cases.
    except HttpError as e:
      print(f'HttpError creating the custom bidding script object: {e}')
      raise Bid2xModelError('HttpError creating the custom bidding script object') from e  # Chain the exception for better context
    except GoogleAPICallError as e:
      print(f'Google API error occurred while creating the custom bidding script object: {e}')
      raise Bid2xModelError('Google API error creating the custom bidding script object') from e  # Chain the exception
    except TimeoutError:
      print(f'Request timed out while creating the custom bidding script object. Please check your network connection.  {e}')
      raise Bid2xModelError('Error creating the custom bidding script object') from e

    # Display the new custom bidding script object.
    if self.debug:
      print(f'The following custom bidding script was created: {response}')

    # Part 4 - Assign script to a custom bidding algorithm.

    # Create the new bid strategy object.
    bidding_strategy = {
        'maximizeSpendAutoBid': {
            'performanceGoalType':
                'BIDDING_STRATEGY_PERFORMANCE_GOAL_TYPE_CUSTOM_ALGO',
            'customBiddingAlgorithmId': algorithm_id
        }
    }

    # Create a line item object assigning the new bid strategy.
    line_item_obj = {'bidStrategy': bidding_strategy}

    # Update the line item with a new bid strategy.
    for li in line_item_array:
      if self.debug:
        print(f'Updating line item: {li}')

      try:
        response = service.advertisers().lineItems().patch(
            advertiserId=f'{advertiser_id}',
            lineItemId=f'{li}',
            updateMask='bidStrategy',
            body=line_item_obj).execute()
      # TODO: b/360401055 - Update HTTPError Exception cases.
      except HttpError as e:
        print(f'HttpError creating algorithm for line item {li}: {e}')
        raise Bid2xModelError('Error creating algorithm for line item') from e
      except GoogleAPICallError as e:
        print(f'Google API error occurred while creating algorithm for line item {li}: {e}')
        raise Bid2xModelError('Error creating algorithm for line item') from e
      except TimeoutError:
        print(f'Request timed out while creating algorithm for line item {li}. Please check your network connection.')
        raise Bid2xModelError('Error creating algorithm for line item') from e

      # Display the line item's new bid strategy.
      print(f'Line Item {response["name"]} is now using the following bid'
          f' strategy: {response["bidStrategy"]}.')

    return True
